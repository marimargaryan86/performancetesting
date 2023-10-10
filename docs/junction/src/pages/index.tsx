import React from 'react';
import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Button from '../components/Button';
import Dots from '../components/Dots';
import HeaderMenu from '../components/HeaderMenu';

import styles from './index.module.css';

function HomepageHeader() {
    const {siteConfig} = useDocusaurusContext();
    return (
        <header className={styles.heroBanner}>
            <div className={styles.heroContainer}>
                <h1>{siteConfig.title}</h1>
                <p>{siteConfig.tagline}</p>
                <Button text="Reseller Documentation" variant="outline" icon="img/arrow.svg" href="/docs/resellers/introduction" />
            </div>
        </header>
    );
}

function WelcomeText() {
    return (
        <section className={styles.welcomeText}>
            <Dots label="How to get in touch"/>
            <section className={styles.headerSection}>
                <h1>Experiencing an issue?</h1>
                <p>
                    Please contact <a className={styles.mailLink} href="mailto:support@snowfalltravel.com">support@snowfalltravel.com</a> if you experience any issues or have questions.
                </p>
                <p>
                    When getting in touch please include the following:
                </p>
            </section>
            <br/>
            <br/>
            <section className={styles.benefitSection}>
                <article className={styles.benefit}>
                    <span className={styles.benefitNumber}>01.</span>
                    <aside className={styles.benefitText}>
                        <span className={styles.benefitTitle}>Description of the problem</span>
                        <span className={styles.benefitDescription}>A description of the problem, and the behavior you expected instead.</span>
                    </aside>
                </article>
                <article className={styles.benefit}>
                    <span className={styles.benefitNumber}>02.</span>
                    <aside className={styles.benefitText}>
                        <span className={styles.benefitTitle}>Describe your dev enviroment</span>
                        <span className={styles.benefitDescription}>Any information regarding your development environment </span>
                    </aside>
                </article>
                <article className={styles.benefit}>
                    <span className={styles.benefitNumber}>03.</span>
                    <aside className={styles.benefitText}>
                        <span className={styles.benefitTitle}>A snippet of code</span>
                        <span className={styles.benefitDescription}>A list of steps and a small snippet of sample code that can be used to reproduce the problem.</span>
                    </aside>
                </article>
                <article className={styles.benefit}>
                    <span className={styles.benefitNumber}>04.</span>
                    <aside className={styles.benefitText}>
                        <span className={styles.benefitTitle}>Output and error messages</span>
                        <span className={styles.benefitDescription}>A description of the expected output and what occurred. Include any error messages you receive.</span>
                    </aside>
                </article>
            </section>
            <Button
                text="View Reseller Documentation"
                variant="filled"
                icon="img/arrow.svg"
                href="/docs/resellers/introduction"
            />
        </section>
    )
}

export default function Home(): JSX.Element {
    return (
        <>
            <HeaderMenu/>
            <HomepageHeader/>
            <WelcomeText/>
        </>
    );
}
