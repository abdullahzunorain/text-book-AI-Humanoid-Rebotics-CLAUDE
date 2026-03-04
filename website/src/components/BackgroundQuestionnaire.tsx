import React, {useState, useCallback} from 'react';

interface BackgroundQuestionnaireProps {
  isOpen: boolean;
  onComplete: () => void;
}

const API_URL =
  (typeof window !== 'undefined' &&
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (window as any).__DOCUSAURUS_CUSTOM_FIELDS?.apiUrl) ||
  'http://localhost:8000';

export default function BackgroundQuestionnaire({
  isOpen,
  onComplete,
}: BackgroundQuestionnaireProps): React.JSX.Element | null {
  const [pythonLevel, setPythonLevel] = useState('beginner');
  const [roboticsExperience, setRoboticsExperience] = useState('none');
  const [mathLevel, setMathLevel] = useState('high_school');
  const [hardwareAccess, setHardwareAccess] = useState(false);
  const [learningGoal, setLearningGoal] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_URL}/api/user/background`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          credentials: 'include',
          body: JSON.stringify({
            python_level: pythonLevel,
            robotics_experience: roboticsExperience,
            math_level: mathLevel,
            hardware_access: hardwareAccess,
            learning_goal: learningGoal.slice(0, 200),
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || 'Failed to save background');
        }

        onComplete();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    },
    [
      pythonLevel,
      roboticsExperience,
      mathLevel,
      hardwareAccess,
      learningGoal,
      onComplete,
    ],
  );

  if (!isOpen) return null;

  return (
    <div className="questionnaire-overlay">
      <form className="questionnaire-form" onSubmit={handleSubmit}>
        <h2>Tell us about yourself</h2>
        <p>Help us personalize your learning experience.</p>

        <div className="questionnaire-field">
          <label htmlFor="q-python">Python Level</label>
          <select
            id="q-python"
            value={pythonLevel}
            onChange={(e) => setPythonLevel(e.target.value)}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div className="questionnaire-field">
          <label htmlFor="q-robotics">Robotics Experience</label>
          <select
            id="q-robotics"
            value={roboticsExperience}
            onChange={(e) => setRoboticsExperience(e.target.value)}>
            <option value="none">None</option>
            <option value="hobbyist">Hobbyist</option>
            <option value="student">Student</option>
            <option value="professional">Professional</option>
          </select>
        </div>

        <div className="questionnaire-field">
          <label htmlFor="q-math">Math Level</label>
          <select
            id="q-math"
            value={mathLevel}
            onChange={(e) => setMathLevel(e.target.value)}>
            <option value="high_school">High School</option>
            <option value="undergraduate">Undergraduate</option>
            <option value="graduate">Graduate</option>
          </select>
        </div>

        <div className="questionnaire-field">
          <label htmlFor="q-hardware">
            <input
              id="q-hardware"
              type="checkbox"
              checked={hardwareAccess}
              onChange={(e) => setHardwareAccess(e.target.checked)}
              style={{marginRight: '0.5rem'}}
            />
            I have access to physical robot hardware
          </label>
        </div>

        <div className="questionnaire-field">
          <label htmlFor="q-goal">Learning Goal (optional, max 200 chars)</label>
          <textarea
            id="q-goal"
            value={learningGoal}
            onChange={(e) => setLearningGoal(e.target.value)}
            maxLength={200}
            placeholder="e.g., Prepare for robotics internship"
          />
        </div>

        {error && <div className="auth-error">{error}</div>}

        <button
          type="submit"
          className="button button--primary"
          disabled={loading}
          style={{width: '100%'}}>
          {loading ? 'Saving...' : 'Save & Continue'}
        </button>
      </form>
    </div>
  );
}
