import axios from "axios";
import {useState} from "react";
import {connect, useDispatch} from "react-redux";
import {LOGIN_FAIL, LOGIN_SUCCESS} from "../../actions/types.jsx";
import { BaseForm } from "../BaseForm/BaseForm.jsx";

export const MainPage = ({isAuthenticated}) => {
    const [err, setErr] = useState("");
    const dispatch = useDispatch();
    const [inCorrectValue, setInCorrectValue] = useState(false);
    const [Data, setData] = useState({
        fio: "",
        email: "",
        password: "",
    });

    const onChange = e => setData({...Data, [e.target.name]: e.target.value});

    const onSubmit = async e => {
        e.preventDefault();
        if (Data.fio.trim() !== '' && Data.email.trim() !== '' && Data.password.trim() !== '') {
            setInCorrectValue(false);
            const formData = {
                fio: Data.fio,
                email: Data.email,
                password: Data.password
            };

            const config = {
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "",
                }
            };

            try {
                // Регистрация
                await axios.post(`http://localhost:8082/api/auth/register`, formData, config);
                // Логин после успешной регистрации
                const loginBody = {
                    email: Data.email,
                    password: Data.password
                };

                const loginResponse = await axios.post(`http://localhost:8082/api/auth/login`, loginBody, config);

                dispatch({
                    type: LOGIN_SUCCESS,
                    payload: loginResponse.data,
                });
            } catch (error) {
                const errorMessage = error.response?.data?.text
                error.message
                "Произошла ошибка";
                setErr(errorMessage);

                if (error.response?.status === 401) {
                    dispatch({
                        type: LOGIN_FAIL,
                    });
                }
            }
        } else {
            setInCorrectValue(true);
        }
    };

    if (isAuthenticated) {
        return <Navigate to="/main" />;
    }

    return (
        <BaseForm
            onSubmit={onSubmit}
            onChange={onChange}
            error={err}
            fields={[
                { name: "fio", type: "text", placeholder: "ФИО", required: true },
                { name: "email", type: "email", placeholder: "Почта", required: true },
                { name: "password", type: "password", placeholder: "Пароль", required: true }
            ]}
            submitText="Зарегистрироваться"
            formTitle="Регистрация"
            reg={true}
            inCorrectValue={inCorrectValue}
        />
    );
};

const mapStateToProps = state => ({
    isAuthenticated: state.auth.isAuthenticated,
});

export default connect(mapStateToProps)(MainPage);