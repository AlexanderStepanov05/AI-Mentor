import Styles from "./Reg.module.css";
import { Link } from "react-router-dom";

export const BaseForm = ({
  onSubmit,
  onChange,
  error,
  fields = [
    { name: "email", type: "email", placeholder: "Почта", required: true },
    { name: "password", type: "password", placeholder: "Пароль", required: true }
  ],
  submitText = "Войти",
  formTitle = "Вход в аккаунт",
  inCorrectValue,
  reg
}) => {
  return (
    <section className={Styles["reg"]}>
      <div className={Styles["container"]}>
        <h1 className={Styles["title"]}>{formTitle}</h1>
        
        <form onSubmit={onSubmit}>
          {fields.map((field) => (
            <div className="form-group" key={field.name}>
              <input
                className="form-control"
                type={field.type}
                placeholder={field.placeholder}
                name={field.name}
                onChange={onChange}
                required={field.required}
              />
            </div>
          ))}
          {inCorrectValue && (
                        <p className={Styles["text"]}>
                            Неправильный формат данных
                        </p>
                    )}
          
          <button className="btn-primary mt-2" type="submit">
            {submitText}
          </button>
          {error && <p style={{ color: 'red' }}>{error}</p>}
        </form>

        {!reg ? (
            <p className={Styles["text"]}>
                Нет аккаунта?{" "}
                <Link className={Styles["link"]} to="/reg">
                    Зарегистрироваться
                </Link>
            </p>
        ) : (
            <p className={Styles["text"]}>
                Уже зарегистрированы?{" "}
                <Link className={Styles["link"]} to="/">
                    Войти в аккаунт
                </Link>
            </p>
        )}
         
      </div>
    </section>
  );
};