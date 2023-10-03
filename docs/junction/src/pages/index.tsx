import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import styles from './index.module.css';

function HomepageHeader() {
    const {siteConfig} = useDocusaurusContext();
    return (
        <div>
            <header className={clsx('hero hero--primary', styles.heroBanner)}>
                <div className="container">
                    <h1 className="hero__title">{siteConfig.title}</h1>
                    <p className="hero__subtitle">{siteConfig.tagline}</p>
                </div>
            </header>
        </div>
    );
}

function WelcomeText() {
    return (
        <div className={styles.welcomeText}>
            <h1>Welcome to the Junction Developer Portal!</h1>
            <br/>
            <p>
                Within this portal you will find documentation, specifications,
                and guides on how best to integrate against Junction APIs.
            </p>
            <br/>

            Please contact <Link
            href={"mailto:support@snowfalltravel.com"}>support@snowfalltravel.com</Link> if
            you experience any issues or have questions.
            <br/>
            <br/>
            <p>
                Please include:
                <ul>
                    <li>A description of the problem, and the behavior you
                        expected instead.
                    </li>
                    <li>A list of steps and a small snippet of sample code that
                        can be used to reproduce the problem.
                    </li>
                    <li>A description of the output you expect and what actually
                        occurred. Include any error messages you receive.
                    </li>
                    <li>Information about your development environment</li>
                </ul>
            </p>
        </div>
    )
}

export default function Home(): JSX.Element {
    return (
        <Layout>
            <HomepageHeader/>
            <WelcomeText></WelcomeText>
            <main></main>
        </Layout>
    );
}
