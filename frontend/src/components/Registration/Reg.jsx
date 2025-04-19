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

    const onSubmit = e => {
        e.preventDefault();
        if (Data.fio.trim() !== '' && Data.email.trim() !== '' && Data.password.trim() !== '') {
            setInCorrectValue(false);
            const formData = {};
            formData.fio = Data.fio;
            formData.email = Data.email;
            formData.password = Data.password;
            axios
                .post(``, formData) // рег
                .then(() => {
                    const body = {};
                    body.username = Data.username;
                    body.password = Data.password;
                    axios
                        .post(``, body) // Логин
                        .then(res => {
                            dispatch({
                                type: LOGIN_SUCCESS,
                                payload: res.data,
                            });
                            const config = {
                                headers: {
                                    "Content-Type": "application/json",
                                    Authorization: `Bearer ${localStorage.getItem("JWTToken")}`,
                                },
                            };
                            const formData = {};
                            formData.tg = Data.tg;
                            axios
                                .patch(`${domain}/editabout`, formData, config)
                                .catch(err => {
                                    setErr(err.response.data.text);
                                });
                        })
                        .catch(err => {
                            console.error(err);
                            setErr(err.response.data.text);
                            dispatch({
                                type: LOGIN_FAIL,
                            });
                        });
                })
                .catch(err => {
                    setErr(err.response.data.text);
                });
        } else{
            setInCorrectValue(true);
        }
    };

    // if (isAuthenticated) {
    //     return <Navigate to="/main"/>;
    // }
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