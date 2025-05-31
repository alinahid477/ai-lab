
// components/AnimatedAILogo.tsx
import React from 'react';

interface AnimatedAILogoProps {
  width?: number;
  height?: number;
}

const AnimatedAILogo: React.FC<AnimatedAILogoProps> = ({ 
  width = 120, 
  height = 40 
}) => {
  return (
    <div 
      className="relative bg-black border-2 border-white rounded-lg overflow-hidden"
      style={{ width, height }}
    >
      {/* Terminal header */}
      <div className="h-2 border-b border-white flex items-center px-1">
        <div className="flex gap-0.5">
          <div className="w-1 h-1 bg-white rounded-full"></div>
          <div className="w-1 h-1 bg-white rounded-full"></div>
          <div className="w-1 h-1 bg-white rounded-full"></div>
        </div>
      </div>
      
      {/* Content area */}
      <div className="relative h-full text-white font-mono text-[6px] leading-tight overflow-hidden">
        {/* AI Badge */}
        <div className="absolute right-1 top-1/2 transform -translate-y-1/2 w-4 h-4 border border-white rounded-full bg-black flex items-center justify-center text-[8px] font-bold z-10">
          AI
        </div>
        
        {/* Header text */}
        <div className="px-1 pt-1 text-[5px] whitespace-nowrap">
          AI SYSTEM ANALYZING...
        </div>
        
        {/* Scrolling logs */}
        <div className="absolute left-1 top-3 animate-scroll-fast">
          <div className="flex flex-col gap-0.5 text-[4px]">
            <div>LOG cc.d.a.xdha..</div>
            <div>LOG auab.c.e.zoza</div>
            <div>LOG LG785.e.rhf..</div>
            <div>LOG Ug.fc.b.a..</div>
            <div>LOG ex.e.t.t2bce.</div>
            <div>LOG ef.b.a.vc.bvu.</div>
            <div>LOG hs.5t.uvzao..</div>
            <div>LOG mn.k8.pxr.qw..</div>
            <div>LOG zb.7y.nmt.45..</div>
            <div>LOG rt.9u.def.xy..</div>
            <div>LOG gh.3i.klm.78..</div>
            <div>LOG vn.6o.abc.12..</div>
            <div>LOG cc.d.a.xdha..</div>
            <div>LOG auab.c.e.zoza</div>
            <div>LOG LG785.e.rhf..</div>
            <div>LOG Ug.fc.b.a..</div>
            <div>LOG ex.e.t.t2bce.</div>
            <div>LOG ef.b.a.vc.bvu.</div>
            <div>LOG hs.5t.uvzao..</div>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        @keyframes scroll-fast {
          0% {
            transform: translateY(20px);
          }
          100% {
            transform: translateY(-60px);
          }
        }
        
        .animate-scroll-fast {
          animation: scroll-fast 1.5s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default AnimatedAILogo;