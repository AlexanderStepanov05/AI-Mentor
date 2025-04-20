import styles from './About.module.css';

export const About = () => {
  return (
    <section className={styles.about} id="about">
      <div className={styles.container}>
        <h2 className={styles.title}>Об университетском AI-ассистенте</h2>
        <div className={styles.content}>
          <div className={styles.text}>
            <p className={styles.paragraph}>
              Наш интеллектуальный помощник создан специально для студентов и преподавателей, 
              чтобы упростить взаимодействие с университетскими процессами.
            </p>
            <p className={styles.paragraph}>
              Используя передовые технологии искусственного интеллекта, ассистент предоставляет 
              мгновенные ответы на организационные вопросы 24/7.
            </p>
            <ul className={styles.features}>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>📅</span>
                Актуальное расписание и изменения
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>💰</span>
                Информация по оплате и стипендиям
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>📚</span>
                Помощь с учебными материалами
              </li>
              <li className={styles.featureItem}>
                <span className={styles.featureIcon}>🏛️</span>
                Информирование по требованиям по предметам
              </li>
            </ul>
          </div>
          <div className={styles.imageWrapper}>
            <div className={styles.image}></div>
          </div>
        </div>
      </div>
    </section>
  );
};
