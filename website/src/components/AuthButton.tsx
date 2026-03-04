import React, {useState, useCallback, useEffect} from 'react';
import {useAuth} from './AuthProvider';
import AuthModal from './AuthModal';
import BackgroundQuestionnaire from './BackgroundQuestionnaire';

/**
 * Auth button for the navbar: shows "Sign In" when logged out,
 * user email + "Sign Out" when logged in.
 *
 * BackgroundQuestionnaire is rendered OUTSIDE the auth-conditional block so it
 * stays mounted even after signup/signin sets isAuthenticated=true.
 *
 * The questionnaire auto-shows whenever the signed-in user has no background
 * profile yet (has_background === false).  It is hidden on sign-out and after
 * successful submission (checkAuth refreshes has_background to true).
 */
export default function AuthButton(): React.JSX.Element {
  const {user, isAuthenticated, loading, signout, checkAuth} = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);

  // Auto-show questionnaire when user is signed in but has no background profile.
  // Covers both the signup flow (new user) and signin for users who never completed
  // the form.  Once checkAuth() refreshes user with has_background=true the effect
  // will not re-fire, so the questionnaire stays closed after a successful submit.
  useEffect(() => {
    if (!loading && isAuthenticated && user?.has_background === false) {
      setShowQuestionnaire(true);
    }
  }, [loading, isAuthenticated, user?.has_background]);

  const handleSignout = useCallback(async () => {
    setShowQuestionnaire(false);
    await signout();
  }, [signout]);

  const handleSignupSuccess = useCallback(() => {
    // Questionnaire is driven by the useEffect above; just close the modal.
    setShowModal(false);
  }, []);

  const handleSigninSuccess = useCallback(() => {
    // Questionnaire is driven by the useEffect above.
    setShowModal(false);
  }, []);

  const handleQuestionnaireComplete = useCallback(() => {
    setShowQuestionnaire(false);
    void checkAuth(); // refresh user → has_background becomes true → effect won't re-trigger
  }, [checkAuth]);

  if (loading) {
    return <span className="navbar__item" style={{opacity: 0.5}}>...</span>;
  }

  return (
    <>
      {/* Auth button — Sign In when logged out, email + Sign Out when logged in */}
      {isAuthenticated && user ? (
        <div className="navbar__item" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
          <span style={{fontSize: '0.875rem', opacity: 0.8}}>{user.email}</span>
          <button
            className="button button--secondary button--sm"
            onClick={handleSignout}
            type="button">
            Sign Out
          </button>
        </div>
      ) : (
        <button
          className="navbar__item button button--primary button--sm"
          onClick={() => setShowModal(true)}
          type="button">
          Sign In
        </button>
      )}

      {/* Modals — rendered unconditionally so they survive auth state changes */}
      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSignupSuccess={handleSignupSuccess}
        onSigninSuccess={handleSigninSuccess}
      />
      <BackgroundQuestionnaire
        isOpen={showQuestionnaire}
        onComplete={handleQuestionnaireComplete}
      />
    </>
  );
}
