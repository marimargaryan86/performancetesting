import React from 'react';
import '../css/dots.css';

interface IProps {
    label?: string;
}

export default function Home({ label }: IProps): JSX.Element {
    return (
        <section className='dots'>
            <img src='img/dots.svg' alt='dots' />
            {label && <span>{label}</span>}
        </section>
    );
}
