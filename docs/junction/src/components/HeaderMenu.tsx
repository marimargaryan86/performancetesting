import React, { useEffect, useState } from 'react';
import '../css/header-menu.css';

export default function Home(): JSX.Element {
    const [scrollPosition, setScrollPosition] = useState(0);

    const handleScroll = () => {
        const currentPosition = window.scrollY;
        setScrollPosition(currentPosition);
    };

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);

        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    return (
        <header
            className={`header-menu ${
                scrollPosition > 0 ? 'header-background' : ''
            }`}
        >
            <a href='/'>
                <img src='/img/snowfall-logo.svg' alt='logo' />
            </a>
            <a href='/docs/resellers/openapi'>API Reference</a>
            <a href='/docs/resellers/guides/create-an-order'>Guides</a>
        </header>
    );
}
