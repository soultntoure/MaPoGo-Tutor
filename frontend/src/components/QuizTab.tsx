
import React, { useState } from 'react';
import { Brain, Loader2, Eye, EyeOff } from 'lucide-react';

interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
}

const QuizTab: React.FC = () => {
  const [quizDifficulty, setQuizDifficulty] = useState('Medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [quiz, setQuiz] = useState<QuizQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [visibleAnswers, setVisibleAnswers] = useState<Set<number>>(new Set());

  const handleGenerateQuiz = async () => {
    setIsLoading(true);
    setQuiz([]);
    setVisibleAnswers(new Set());

    try {
      const response = await fetch('http://localhost:5000/quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          difficulty: quizDifficulty,
          num_questions: parseInt(numQuestions.toString()),
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setQuiz(data.quiz);
      } else {
        console.error('Error generating quiz:', data.error);
      }
    } catch (error) {
      console.error('Network error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAnswer = (questionIndex: number) => {
    const newVisibleAnswers = new Set(visibleAnswers);
    if (newVisibleAnswers.has(questionIndex)) {
      newVisibleAnswers.delete(questionIndex);
    } else {
      newVisibleAnswers.add(questionIndex);
    }
    setVisibleAnswers(newVisibleAnswers);
  };

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-[#333333] flex items-center space-x-2">
        <Brain className="w-5 h-5" />
        <span>Generate a Quiz</span>
      </h3>

      {/* Quiz Options */}
      <div className="bg-gray-50 p-4 rounded-lg space-y-4">
        <h4 className="font-medium text-gray-700">Options</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Difficulty:
            </label>
            <select
              value={quizDifficulty}
              onChange={(e) => setQuizDifficulty(e.target.value)}
              className="w-full px-3 py-2 border border-gray-light rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Questions:
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value) || 5)}
              className="w-full px-3 py-2 border border-gray-light rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>

        <button
          onClick={handleGenerateQuiz}
          disabled={isLoading}
          className={`
            px-6 py-2 rounded-lg font-medium transition-all duration-200
            ${isLoading 
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
              : 'bg-primary text-white hover:bg-blue-600 hover:shadow-md'
            }
          `}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Generating Quiz...</span>
            </div>
          ) : (
            'Generate Quiz'
          )}
        </button>
      </div>

      {/* Quiz Results */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-12 text-gray-600">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
              <p>Generating your quiz...</p>
            </div>
          </div>
        ) : quiz.length > 0 ? (
          <div className="space-y-6">
            <h4 className="text-lg font-semibold text-gray-700">
              Quiz Results ({quiz.length} questions)
            </h4>
            
            {quiz.map((question, questionIndex) => (
              <div
                key={questionIndex}
                className="border border-gray-light rounded-lg p-5 bg-white shadow-sm"
              >
                <div className="space-y-4">
                  <h5 className="font-semibold text-gray-800 text-lg">
                    {questionIndex + 1}. {question.question}
                  </h5>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {question.options.map((option, optionIndex) => (
                      <div
                        key={optionIndex}
                        className={`
                          p-3 rounded-lg border transition-colors duration-200
                          ${visibleAnswers.has(questionIndex) && option === question.answer
                            ? 'bg-green-100 border-green-300 text-green-800'
                            : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                          }
                        `}
                      >
                        <span className="font-medium mr-2">
                          {String.fromCharCode(65 + optionIndex)}.
                        </span>
                        {option}
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={() => toggleAnswer(questionIndex)}
                    className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-primary hover:bg-blue-50 rounded-lg transition-colors duration-200"
                  >
                    {visibleAnswers.has(questionIndex) ? (
                      <>
                        <EyeOff className="w-4 h-4" />
                        <span>Hide Answer</span>
                      </>
                    ) : (
                      <>
                        <Eye className="w-4 h-4" />
                        <span>Show Answer</span>
                      </>
                    )}
                  </button>

                  {visibleAnswers.has(questionIndex) && (
                    <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                      <span className="font-medium text-green-800">
                        Correct Answer: {question.answer}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center py-12 text-gray-500">
            <div className="text-center">
              <Brain className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>Configure your quiz options and click "Generate Quiz" to start.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuizTab;
