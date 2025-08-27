'use client';

import React, { useState, useRef, useCallback } from 'react';

interface ResizableLayoutProps {
  leftPanel: React.ReactNode;
  centerPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  leftInitialWidth?: number;
  rightInitialWidth?: number;
  leftMinWidth?: number;
  rightMinWidth?: number;
  leftMaxWidth?: number;
  rightMaxWidth?: number;
  rightVisible?: boolean;
  leftCollapsed?: boolean;
  onToggleRightPanel?: () => void;
}

const ResizableLayout: React.FC<ResizableLayoutProps> = ({
  leftPanel,
  centerPanel,
  rightPanel,
  leftInitialWidth = 256,
  rightInitialWidth = 320,
  leftMinWidth = 200,
  rightMinWidth = 280,
  leftMaxWidth = 500,
  rightMaxWidth = 600,
  rightVisible = true,
  leftCollapsed = false,
  onToggleRightPanel
}) => {
  const [leftWidth, setLeftWidth] = useState(leftCollapsed ? 56 : leftInitialWidth);
  const [rightWidth, setRightWidth] = useState(rightInitialWidth);
  const [isResizingLeft, setIsResizingLeft] = useState(false);
  const [isResizingRight, setIsResizingRight] = useState(false);
  
  React.useEffect(() => {
    setLeftWidth(leftCollapsed ? 56 : leftInitialWidth);
  }, [leftCollapsed, leftInitialWidth]);
  
  const leftResizerRef = useRef<HTMLDivElement>(null);
  const rightResizerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback((side: 'left' | 'right') => (e: React.MouseEvent) => {
    e.preventDefault();
    if (side === 'left') {
      setIsResizingLeft(true);
    } else if (side === 'right') {
      setIsResizingRight(true);
    }
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isResizingLeft) {
      const newWidth = Math.min(
        Math.max(e.clientX, 56), // 最小宽度为折叠态的56px
        leftMaxWidth
      );
      setLeftWidth(newWidth);
    }
    
    if (isResizingRight && rightVisible) {
      const newWidth = Math.min(
        Math.max(window.innerWidth - e.clientX, rightMinWidth),
        rightMaxWidth
      );
      setRightWidth(newWidth);
    }
  }, [isResizingLeft, isResizingRight, leftMaxWidth, rightMinWidth, rightMaxWidth, rightVisible]);

  const handleMouseUp = useCallback(() => {
    setIsResizingLeft(false);
    setIsResizingRight(false);
  }, []);

  React.useEffect(() => {
    if (isResizingLeft || isResizingRight) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isResizingLeft, isResizingRight, handleMouseMove, handleMouseUp]);

  return (
    <div className="min-h-screen bg-gray-50 flex relative">
      {/* Left Panel */}
      <div 
        className="bg-white shadow-sm border-r border-gray-200 flex flex-col transition-none"
        style={{ 
          width: `${leftWidth}px`, 
          minWidth: leftCollapsed ? '56px' : `${leftMinWidth}px`, 
          maxWidth: `${leftMaxWidth}px` 
        }}
      >
        {leftPanel}
      </div>

      {/* Left Resizer - Always show */}
      <div
        ref={leftResizerRef}
        className={`w-1 bg-gray-200 hover:bg-blue-400 cursor-col-resize flex-shrink-0 transition-all duration-200 relative group ${
          isResizingLeft ? 'bg-blue-500 w-1' : ''
        }`}
        onMouseDown={handleMouseDown('left')}
      >
        <div className="absolute inset-0 w-3 -mx-1" />
        <div className="absolute inset-y-0 left-0 w-1 bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity rounded-full" />
      </div>

      {/* Center Panel */}
      <div className="flex-1 min-w-0 relative">
        {centerPanel}
        
        {/* Right panel expand button when collapsed */}
        {!rightVisible && onToggleRightPanel && (
          <button
            onClick={onToggleRightPanel}
            className="absolute top-4 right-4 p-2 bg-blue-600 text-white rounded-lg shadow-lg hover:bg-blue-700 transition-all duration-200 z-10"
            title="显示预览面板"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>

      {/* Right Resizer - Only show when right panel is visible */}
      {rightVisible && (
        <div
          ref={rightResizerRef}
          className={`w-1 bg-gray-200 hover:bg-blue-400 cursor-col-resize flex-shrink-0 transition-all duration-200 relative group ${
            isResizingRight ? 'bg-blue-500 w-1' : ''
          }`}
          onMouseDown={handleMouseDown('right')}
        >
          <div className="absolute inset-0 w-3 -mx-1" />
          <div className="absolute inset-y-0 left-0 w-1 bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity rounded-full" />
        </div>
      )}

      {/* Right Panel */}
      {rightVisible && (
        <div 
          className="bg-white border-l border-gray-200 flex flex-col transition-none"
          style={{ width: `${rightWidth}px`, minWidth: `${rightMinWidth}px`, maxWidth: `${rightMaxWidth}px` }}
        >
          {rightPanel}
        </div>
      )}
    </div>
  );
};

export default ResizableLayout;