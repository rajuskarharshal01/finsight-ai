import React from 'react';

const LoadingSpinner = ({ message = 'Researching...' }) => {
    return (
        <div style={styles.container}>
            <div style={styles.spinner}></div>
            <p style={styles.message}>{message}</p>
            <p style={styles.sub}>AI agent is gathering financial data</p>
            <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px',
        gap: '16px',
    },
    spinner: {
        width: '48px',
        height: '48px',
        border: '4px solid #0f3460',
        borderTop: '4px solid #00d4aa',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
    },
    message: {
        color: '#00d4aa',
        fontSize: '18px',
        fontWeight: '600',
        animation: 'pulse 2s ease-in-out infinite',
        margin: 0,
    },
    sub: {
        color: '#8892b0',
        fontSize: '13px',
        margin: 0,
    },
};

export default LoadingSpinner;