import React from 'react';

const FollowingCard = ({ following, showFollowingCard, toggleFollowingCard }) => {
  return (
    <>
      {showFollowingCard && (
        <div className="fixed top-0 left-0 w-full h-full flex justify-center items-center">
          <div className="bg-black bg-opacity-50 absolute top-0 left-0 w-full h-full" onClick={toggleFollowingCard}></div>
          <div className="bg-white shadow-lg rounded-lg p-8 w-96 max-h-96 overflow-y-auto relative">
            <button onClick={toggleFollowingCard} className="absolute top-2 right-2 text-gray-500 hover:text-gray-700">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <h2 className="text-xl font-bold mb-4">Following</h2>
            <ul className="divide-y divide-gray-200">
              {following.map((follow, index) => (
                <li key={index} className="py-2">
                  <a href={`/users/${follow}`}>{follow}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </>
  );
};

export default FollowingCard;
