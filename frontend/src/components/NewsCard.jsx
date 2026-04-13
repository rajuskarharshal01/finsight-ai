import React from 'react';
const NewsCard = ({ articles }) => {
    if (!articles || articles.length === 0) {
        return <div style={{ color: '#8892b0', textAlign: 'center', padding: '20px' }}>No news available</div>;
    }
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {articles.map((article, index) => (
                <div key={index} style={{ background: '#16213e', border: '1px solid #0f3460', borderRadius: '8px', padding: '16px', borderLeft: '3px solid #00d4aa' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ color: '#00d4aa', fontSize: '12px', fontWeight: '600', textTransform: 'uppercase' }}>{article.source}</span>
                        <span style={{ color: '#8892b0', fontSize: '12px' }}>{article.published?.slice(0, 16) || ''}</span>
                    </div>
                    <p style={{ color: '#ccd6f6', fontSize: '14px', lineHeight: '1.5', margin: '0 0 8px 0' }}>{article.title}</p>
                    {article.link && (
                        <a href={article.link} target="_blank" rel="noopener noreferrer" style={{ color: '#00d4aa', fontSize: '13px', textDecoration: 'none' }}>
                            Read more →
                        </a>
                    )}
                </div>
            ))}
        </div>
    );
};
export default NewsCard;