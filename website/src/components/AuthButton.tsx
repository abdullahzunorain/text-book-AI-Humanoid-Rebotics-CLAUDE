import React, {useState, useCallback} from 'react';
import {useAuth} from './AuthProvider';
import AuthModal from './AuthModal';
import BackgroundQuestionnaire from './BackgroundQuestionnaire';

/**
 * Auth button for the navbar: shows "Sign In" when logged out,
 * user email + "Sign Out" when logged in.
 */
export default function AuthButton(): React.JSX.Element {
  const {user, isAuthenticated, loading, signout, checkAuth} = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [showQuestionnaire, setShowQuestionnaire] = useState(false);

  const handleSignout = useCallback(async () => {
    await signout();
  }, [signout]);

  const handleSignupSuccess = useCallback(() => {
    setShowModal(false);
    setShowQuestionnaire(true);
  }, []);

  const handleQuestionnaireComplete = useCallback(() => {
    setShowQuestionnaire(false);
    checkAuth();
  }, [checkAuth]);

  if (loading) {
    return <span className="navbar__item" style={{opacity: 0.5}}>...</span>;
  }

  if (isAuthenticated && user) {
    return (
      <div className="navbar__item" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
        <span style={{fontSize: '0.875rem', opacity: 0.8}}>{user.email}</span>
        <button
          className="button button--secondary button--sm"
          onClick={handleSignout}
          type="button">
          Sign Out
        </button>
      </div>
    );
  }

  return (
    <>
      <button
        className="navbar__item button button--primary button--sm"
        onClick={() => setShowModal(true)}
        type="button">
        Sign In
      </button>
      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSignupSuccess={handleSignupSuccess}
      />
      <BackgroundQuestionnaire
        isOpen={showQuestionnaire}
        onComplete={handleQuestionnaireComplete}
      />
    </>
  );
}
