import React from 'react';

export const Skeleton = ({ className, style }) => (
  <div className={`skeleton ${className || ''}`} style={style} />
);

export const SkeletonCard = () => (
  <div className="card">
    <Skeleton className="skeleton-text" style={{ width: '40%' }} />
    <Skeleton className="skeleton-stat" />
  </div>
);

export const SkeletonTable = ({ rows = 5, cols = 4 }) => (
  <div className="table-wrapper">
    <table>
      <thead>
        <tr>
          {Array.from({ length: cols }).map((_, i) => (
            <th key={i}><Skeleton className="skeleton-text" style={{ width: '80%', height: '0.8rem' }} /></th>
          ))}
        </tr>
      </thead>
      <tbody>
        {Array.from({ length: rows }).map((_, i) => (
          <tr key={i}>
            {Array.from({ length: cols }).map((_, j) => (
              <td key={j}><Skeleton className="skeleton-text" style={{ height: '1.2rem' }} /></td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
