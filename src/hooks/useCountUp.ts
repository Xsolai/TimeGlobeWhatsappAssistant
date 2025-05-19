import { useState, useEffect, useRef } from 'react';

interface UseCountUpProps {
  end: number;
  duration?: number;
  startOnMount?: boolean;
  decimalPlaces?: number;
}

const easeOutExpo = (t: number): number => {
  return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
};

const useCountUp = ({
  end,
  duration = 2000,
  startOnMount = true,
  decimalPlaces = 0,
}: UseCountUpProps): string => {
  const [count, setCount] = useState(0);
  const frameRate = 1000 / 60; // 60 FPS
  const totalFrames = Math.round(duration / frameRate);
  const animationFrameId = useRef<number | null>(null);
  const isMounted = useRef(true);
  const hasStarted = useRef(false);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, []);

  useEffect(() => {
    if (startOnMount && !hasStarted.current) {
      let frame = 0;
      hasStarted.current = true;

      const counter = () => {
        frame++;
        const progress = easeOutExpo(frame / totalFrames);
        const currentNum = progress * end;
        
        if (isMounted.current) {
          setCount(currentNum);
        }

        if (frame < totalFrames && isMounted.current) {
          animationFrameId.current = requestAnimationFrame(counter);
        } else {
          if (isMounted.current) {
            setCount(end); // Ensure it ends exactly on the target
            hasStarted.current = false; // Allow restart if end value changes and startOnMount is true
          }
          if (animationFrameId.current) {
            cancelAnimationFrame(animationFrameId.current);
          }
        }
      };
      animationFrameId.current = requestAnimationFrame(counter);
    }
     // Reset and restart animation if the 'end' value changes after initial mount & animation
    // and startOnMount is true. This is useful if data loads and then updates.
    else if (startOnMount && hasStarted.current && end !== count ) { 
        hasStarted.current = false; // Reset for re-animation
        setCount(0); // Reset count before starting new animation
         // Small timeout to allow state to reset before restarting
        setTimeout(() => {
            if(isMounted.current && !hasStarted.current) { // Check again to prevent race conditions
                let frame = 0;
                hasStarted.current = true;
                const counter = () => {
                    frame++;
                    const progress = easeOutExpo(frame / totalFrames);
                    const currentNum = progress * end;
                    if(isMounted.current) setCount(currentNum);
                    if (frame < totalFrames && isMounted.current) {
                        animationFrameId.current = requestAnimationFrame(counter);
                    } else {
                        if(isMounted.current) setCount(end);
                        hasStarted.current = false;
                        if (animationFrameId.current) cancelAnimationFrame(animationFrameId.current);
                    }
                };
                animationFrameId.current = requestAnimationFrame(counter);
            }
        }, 50);


    }


    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
      hasStarted.current = false; // Reset on unmount or if dependencies change triggering re-render
    };
  }, [end, duration, startOnMount, totalFrames]); // Rerun effect if these change

  return count.toFixed(decimalPlaces);
};

export default useCountUp; 