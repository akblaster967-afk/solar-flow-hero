import React from 'react';

export function SolarHero() {
  const benefits = [
    {
      title: 'Lower monthly bills',
      description: 'Offset high utility costs with clean power that works around the clock when the sun is shining.',
      value: 'Up to 40%'
    },
    {
      title: 'Cleaner, smarter energy',
      description: 'Reduce dependence on fossil fuels while adding a more resilient home energy setup.',
      value: 'Carbon down'
    },
    {
      title: 'Built for long-term value',
      description: 'Modern panels and battery-ready systems increase property value and energy independence.',
      value: '25-year life'
    }
  ];

  const stats = [
    { label: 'Average savings', value: '$157/mo' },
    { label: 'Typical system', value: '8.4 kW' },
    { label: 'Tax credit potential', value: '30%' }
  ];

  return (
    <>
      <section className="solar-hero" aria-label="How solar works">
        <div className="solar-hero__grid" aria-hidden="true" />
        <div className="solar-hero__inner">
          <span className="solar-hero__eyebrow">How Solar Works</span>
          <h1 className="solar-hero__title">
            From Sunlight to <span className="accent">Savings</span>, in Four Steps
          </h1>
          <p className="solar-hero__subtitle">
            See the journey: sunlight hits your panels, the inverter turns it into
            power your home can use, and the meter spins your savings forward.
          </p>

          <div className="solar-hero__actions" aria-label="Call to action">
            <a className="solar-hero__button solar-hero__button--primary" href="#estimate">
              Get a free quote
            </a>
            <a className="solar-hero__button solar-hero__button--ghost" href="#savings">
              See savings
            </a>
          </div>

          <div className="solar-hero__stats" aria-label="Solar performance summary">
            {stats.map((item) => (
              <div className="solar-hero__stat" key={item.label}>
                <strong>{item.value}</strong>
                <span>{item.label}</span>
              </div>
            ))}
          </div>

          {/* ---------- Infographic SVG ---------- */}
          <svg
            className="solar-hero__diagram"
            viewBox="0 0 1200 420"
            role="img"
            aria-labelledby="flowTitle flowDesc"
            xmlns="http://www.w3.org/2000/svg"
          >
            <title id="flowTitle">Solar energy flow: Sun to Panel to Inverter to Home to Savings</title>
            <desc id="flowDesc">
              An infographic showing solar energy traveling from the sun, into roof
              solar panels, through an inverter that converts DC to AC, powering a
              home, and finally delivering bill savings.
            </desc>

            <defs>
              <linearGradient id="sh-amber" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#ffd166" />
                <stop offset="100%" stopColor="#ffb347" />
              </linearGradient>
              <linearGradient id="sh-panel" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#1d4d89" />
                <stop offset="100%" stopColor="#123a6b" />
              </linearGradient>
              <linearGradient id="sh-inverter" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2a4a55" />
                <stop offset="100%" stopColor="#1c353d" />
              </linearGradient>
              <linearGradient id="sh-home" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#eef7f3" />
                <stop offset="100%" stopColor="#d4e9e0" />
              </linearGradient>
              <radialGradient id="sh-sunglow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#ffe0a3" stopOpacity="0.9" />
                <stop offset="60%" stopColor="#ffb347" stopOpacity="0.35" />
                <stop offset="100%" stopColor="#ffb347" stopOpacity="0" />
              </radialGradient>
              <linearGradient id="sh-green" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#3ddc97" />
                <stop offset="100%" stopColor="#2bbf80" />
              </linearGradient>
              <marker id="sh-arr-amber" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 Z" fill="#ffb347" />
              </marker>
              <marker id="sh-arr-green" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
                <path d="M0,0 L6,3 L0,6 Z" fill="#3ddc97" />
              </marker>
            </defs>

            <g className="sh-connector sh-connector--1">
              <line x1="150" y1="150" x2="305" y2="150" stroke="#ffb347" strokeWidth="2" opacity="0.18" />
              <line className="sh-flow sh-flow--dc" x1="150" y1="150" x2="305" y2="150"
                stroke="#ffd166" strokeWidth="2.5" markerEnd="url(#sh-arr-amber)" />
            </g>
            <g className="sh-connector sh-connector--2">
              <line x1="495" y1="150" x2="625" y2="150" stroke="#ffd166" strokeWidth="2" opacity="0.18" />
              <line className="sh-flow sh-flow--dc" x1="495" y1="150" x2="625" y2="150"
                stroke="#ffd166" strokeWidth="2.5" markerEnd="url(#sh-arr-amber)" />
            </g>
            <g className="sh-connector sh-connector--3">
              <line x1="815" y1="150" x2="945" y2="150" stroke="#3ddc97" strokeWidth="2" opacity="0.18" />
              <line className="sh-flow sh-flow--ac" x1="815" y1="150" x2="945" y2="150"
                stroke="#3ddc97" strokeWidth="2.5" markerEnd="url(#sh-arr-green)" />
            </g>
            <g className="sh-connector sh-connector--4">
              <line x1="1030" y1="200" x2="1090" y2="285" stroke="#3ddc97" strokeWidth="2" opacity="0.18" />
              <line className="sh-flow sh-flow--save" x1="1030" y1="200" x2="1090" y2="285"
                stroke="#3ddc97" strokeWidth="2.5" markerEnd="url(#sh-arr-green)" />
            </g>

            <g className="sh-node sh-node--1">
              <circle className="sh-sun-glow" cx="105" cy="150" r="58" fill="url(#sh-sunglow)" />
              <g className="sh-sun-rays">
                {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
                  <line className="sh-ray" key={deg}
                    x1="105" y1="78" x2="105" y2="62"
                    stroke="#ffb347" strokeWidth="3" strokeLinecap="round"
                    transform={`rotate(${deg} 105 150)`} />
                ))}
              </g>
              <circle cx="105" cy="150" r="32" fill="url(#sh-amber)" />
              <circle cx="105" cy="150" r="32" fill="none" stroke="#ffe0a3" strokeWidth="1.5" opacity="0.6" />
            </g>
            <g className="sh-label sh-label--1">
              <text x="105" y="232" textAnchor="middle" fill="#f1fbf8" fontSize="15" fontWeight="700">
                Sunlight
              </text>
              <text x="105" y="252" textAnchor="middle" fill="#9fb8b2" fontSize="12">
                Free &amp; unlimited
              </text>
            </g>

            <g className="sh-node sh-node--2">
              <rect x="305" y="115" width="190" height="70" rx="8" fill="url(#sh-panel)"
                stroke="#2a6bc7" strokeWidth="1.5" />
              {[325, 365, 405, 445].map((x) => (
                <g key={x}>
                  <line x1={x} y1="115" x2={x} y2="185" stroke="#0f2d57" strokeWidth="2" />
                  <line x1="305" y1="150" x2="495" y2="150" stroke="#0f2d57" strokeWidth="2" />
                </g>
              ))}
              <rect x="305" y="115" width="190" height="32" rx="8" fill="#ffffff" opacity="0.06" />
              <rect x="392" y="185" width="16" height="22" fill="#1c353d" />
            </g>
            <g className="sh-label sh-label--2">
              <text x="400" y="232" textAnchor="middle" fill="#f1fbf8" fontSize="15" fontWeight="700">
                Solar Panels
              </text>
              <text x="400" y="252" textAnchor="middle" fill="#9fb8b2" fontSize="12">
                Capture DC current
              </text>
            </g>

            <g className="sh-node sh-node--3">
              <rect x="625" y="115" width="190" height="70" rx="10" fill="url(#sh-inverter)"
                stroke="#3ddc97" strokeWidth="1.5" strokeOpacity="0.4" />
              <path className="sh-wave"
                d="M645 150 Q655 130 665 150 T685 150 T705 150 T725 150 T745 150 T765 150 T785 150 T805 150"
                fill="none" stroke="#3ddc97" strokeWidth="2.2" strokeLinecap="round" />
              <rect x="770" y="123" width="36" height="18" rx="4" fill="rgba(61,220,151,0.15)" />
              <text x="788" y="136" textAnchor="middle" fill="#3ddc97" fontSize="11" fontWeight="700">AC</text>
              <rect x="770" y="160" width="36" height="18" rx="4" fill="rgba(255,179,71,0.15)" />
              <text x="788" y="173" textAnchor="middle" fill="#ffb347" fontSize="11" fontWeight="700">DC</text>
            </g>
            <g className="sh-label sh-label--3">
              <text x="720" y="232" textAnchor="middle" fill="#f1fbf8" fontSize="15" fontWeight="700">
                Inverter
              </text>
              <text x="720" y="252" textAnchor="middle" fill="#9fb8b2" fontSize="12">
                Converts DC to AC
              </text>
            </g>

            <g className="sh-node sh-node--4">
              <rect x="945" y="115" width="85" height="85" rx="8" fill="url(#sh-home)" />
              <path d="M935 115 L987 80 L1040 115 Z" fill="#2bbf80" />
              <rect x="975" y="155" width="22" height="45" rx="3" fill="#1c353d" />
              <rect x="953" y="128" width="16" height="16" rx="2" fill="#3ddc97" opacity="0.85" />
              <rect x="1005" y="128" width="16" height="16" rx="2" fill="#3ddc97" opacity="0.5" />
            </g>
            <g className="sh-label sh-label--4">
              <text x="987" y="232" textAnchor="middle" fill="#f1fbf8" fontSize="15" fontWeight="700">
                Your Home
              </text>
              <text x="987" y="252" textAnchor="middle" fill="#9fb8b2" fontSize="12">
                Powered by the sun
              </text>
            </g>

            <g className="sh-node sh-node--5">
              <g className="sh-coin">
                <circle cx="1095" cy="315" r="42" fill="url(#sh-green)" />
                <circle cx="1095" cy="315" r="42" fill="none" stroke="#a6f0d2" strokeWidth="1.5" opacity="0.5" />
                <text x="1095" y="310" textAnchor="middle" fill="#0a1f1c" fontSize="22" fontWeight="800">$</text>
                <text x="1095" y="330" textAnchor="middle" fill="#0a1f1c" fontSize="10" fontWeight="700" letterSpacing="1">SAVED</text>
              </g>
            </g>
            <g className="sh-label sh-label--5">
              <text x="1095" y="382" textAnchor="middle" fill="#3ddc97" fontSize="15" fontWeight="700">
                Bill Savings
              </text>
              <text x="1095" y="402" textAnchor="middle" fill="#9fb8b2" fontSize="12">
                Lower monthly costs
              </text>
            </g>
          </svg>

          <div className="solar-hero__legend">
            <span className="sh-leg">
              <span className="sh-leg__dot" style={{ background: '#ffd166' }} />
              Sunlight
            </span>
            <span className="sh-leg">
              <span className="sh-leg__dot" style={{ background: '#1d4d89' }} />
              Solar Panels (DC)
            </span>
            <span className="sh-leg">
              <span className="sh-leg__dot" style={{ background: '#3ddc97' }} />
              Inverter (AC) → Home
            </span>
            <span className="sh-leg">
              <span className="sh-leg__dot" style={{ background: '#2bbf80' }} />
              Savings
            </span>
          </div>
        </div>
      </section>

      <section className="solar-landing" id="savings">
        <div className="solar-landing__inner">
          <div className="solar-landing__header">
            <span className="solar-landing__eyebrow">Why homeowners switch</span>
            <h2>Make sunlight pay for itself.</h2>
          </div>

          <div className="solar-landing__grid">
            {benefits.map((item) => (
              <article className="solar-landing__card" key={item.title}>
                <span className="solar-landing__badge">{item.value}</span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="solar-proof" id="estimate">
        <div className="solar-proof__inner">
          <div className="solar-proof__card">
            <div>
              <span className="solar-proof__tag">Trusted results</span>
              <h3>Homes like yours are cutting bills and locking in cleaner power.</h3>
            </div>
            <div className="solar-proof__numbers">
              <div>
                <strong>4.9/5</strong>
                <span>Average client rating</span>
              </div>
              <div>
                <strong>1,200+</strong>
                <span>Installations completed</span>
              </div>
              <div>
                <strong>14 days</strong>
                <span>Typical project timeline</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="solar-cta">
        <div className="solar-cta__inner">
          <div>
            <span className="solar-cta__eyebrow">Ready when you are</span>
            <h3>Start planning your solar savings today.</h3>
          </div>
          <a href="#top" className="solar-cta__button">Book a free assessment</a>
        </div>
      </section>
    </>
  );
}

export default SolarHero;
