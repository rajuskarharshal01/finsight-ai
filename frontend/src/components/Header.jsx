import React from 'react';

const Header = ({ onNavigate, currentPage }) => {
    return (
        <header style={styles.header}>
            <div style={styles.brand}>
                <span style={styles.logo}>📈</span>
                <span style={styles.title}>FinSight AI</span>
                <span style={styles.subtitle}>Financial Research Agent</span>
            </div>
            <nav style={styles.nav}>
                <button
                    style={{
                        ...styles.navBtn,
                        ...(currentPage === 'home' ? styles.navBtnActive : {})
                    }}
                    onClick={() => onNavigate('home')}
                >
                    Dashboard
                </button>
                <button
                    style={{
                        ...styles.navBtn,
                        ...(currentPage === 'analysis' ? styles.navBtnActive : {})
                    }}
                    onClick={() => onNavigate('analysis')}
                >
                    Analysis
                </button>
            </nav>
        </header>
    );
};

const styles = {
    header: {
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        padding: '16px 32px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid #0f3460',
        boxShadow: '0 2px 20px rgba(0,0,0,0.3)',
    },
    brand: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
    },
    logo: {
        fontSize: '28px',
    },
    title: {
        color: '#00d4aa',
        fontSize: '22px',
        fontWeight: '700',
        letterSpacing: '1px',
    },
    subtitle: {
        color: '#8892b0',
        fontSize: '13px',
        marginLeft: '4px',
    },
    nav: {
        display: 'flex',
        gap: '8px',
    },
    navBtn: {
        background: 'transparent',
        border: '1px solid #0f3460',
        color: '#8892b0',
        padding: '8px 20px',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '14px',
        transition: 'all 0.2s',
    },
    navBtnActive: {
        background: '#00d4aa22',
        border: '1px solid #00d4aa',
        color: '#00d4aa',
    },
};

export default Header;