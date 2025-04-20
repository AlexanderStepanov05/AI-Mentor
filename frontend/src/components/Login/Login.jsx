import axios from "axios";
import React, { useState } from "react";
import { connect, useDispatch } from "react-redux";
import { LOGIN_SUCCESS } from "../../actions/types.jsx";
// import domain from "../../domain.js";
import { BaseForm } from "../BaseForm/BaseForm.jsx";

export const Login = ({ isAuthenticated }) => {
    const [err, setErr] = useState("");
    const dispatch = useDispatch();
    const [inCorrectValue, setInCorrectValue] = useState(false);
    const [Data, setData] = useState({
        email: "",
        password: "",
    });

    const onChange = e => setData({ ...Data, [e.target.name]: e.target.value });

    const onSubmit = e => {
        e.preventDefault();
        if (Data.email.trim() !== "" && Data.password.trim() !== "") {
            setInCorrectValue(false);
            const formData = {};
            formData.email = Data.email;
            formData.password = Data.password;
            axios
                .post(`http://localhost:8082/api/auth/login`, formData)
                .then(res => {
                    dispatch({
                        type: LOGIN_SUCCESS,
                        payload: res.data,
                    });
                })
                .catch(err => {
                    setErr(err.response.data.text);
                });
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
            reg={false}
            inCorrectValue={inCorrectValue}
        />
    );
}

const mapStateToProps = state => ({
    isAuthenticated: state.auth.isAuthenticated,
});

export default connect(mapStateToProps)(Login);