import React from "react";
import '../css/button.css';

export default function Home(props): JSX.Element {
    const text = props.text;
    const variant: 'outline' | 'filled' = props.variant;
    const href: string | undefined = props.href;
    const icon: string | undefined = props.icon;

    return (
        <a className={`${variant} button`} href={href}>
            {
                icon ? (<img src={icon} alt="icon"/>) : (<></>)
            }
            {text}
        </a>
    );
}
