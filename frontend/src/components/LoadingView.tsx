import React, { useEffect, useState } from 'react';

const stages = [
  'Identifying relevant scientific domains & principles...',
  'Traversing knowledge graph & verifying dimensional formulas...',
  'Formulating reasoning DAG & evaluating structural dependencies...',
  'Evaluating analogical schema projection & applicability guard...',
  'Executing empirical hypothesis verification & dimensional checks...',
];

export const LoadingView: React.FC = () => {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStageIndex((prev) => (prev + 1) % stages.length);
    }, 750);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex-1 flex flex-col justify-center items-center py-24 px-4 w-full max-w-xl mx-auto text-center">
      {/* Refined Minimalist Spinner */}
      <div className="w-10 h-10 border-2 border-gray-100 border-t-blue-600 rounded-full animate-spin mb-6" />

      <h3 className="text-base font-semibold text-gray-900 mb-2">
        AXION is investigating...
      </h3>
      <p className="text-xs text-gray-500 font-mono tracking-wide h-6">
        {stages[stageIndex]}
      </p>
    </div>
  );
};
