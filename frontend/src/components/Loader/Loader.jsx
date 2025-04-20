import { useState, useEffect } from "react";
export default function Loader() {
    const [dots, setDots] = useState('.');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prevDots => {
        if (prevDots === '.') return '..';
        if (prevDots === '..') return '...';
        return '.';
      });
    }, 500); 

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
        fontSize: '24px',
        fontFamily: 'monospace',
        display: 'inline-block',
        width: '50px',
        textAlign: 'left'
      }}>
        {dots}
      </div>
  )
}