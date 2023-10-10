import React from "react";
import '../css/dots.css';

export default function Home(props): JSX.Element {
    const label = props.label;

    return (
        <section className="dots">
            <img src="img/dots.svg" alt="dots"/>
            <span>
                {label}
            </span>
        </section>
    );
}
