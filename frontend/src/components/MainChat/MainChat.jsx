import { useState, useRef, useEffect } from "react";
import { useDispatch } from "react-redux";
import {LOGOUT} from "../../actions/types.jsx";
import style from "./MainChat.module.css";
import rightArrow from "../../assets/rightArrow.svg";
import axios from "axios";
import Loader from "../Loader/Loader";


export const MainChat = () => {
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const textareaRef = useRef(null);
    const [answers, setAnswers] = useState([]);
    const dispatch = useDispatch();

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            const newHeight = textareaRef.current.scrollHeight;
            textareaRef.current.style.height = `${newHeight}px`;
            textareaRef.current.style.overflowY = newHeight > 400 ? 'auto' : 'hidden';
        }
    }, [message]);

    
    const handleChange = (e) => {
        setMessage(e.target.value);
    };

    const handleSubmit = () => {

        if (!message.trim()) return;
        setLoading(true);
        
        const formData = new FormData();
        formData.append('chat', message);
        setMessage('');
        setAnswers(prev => [...prev, {
            my: message,
        }])
        const config = {
            headers: {
                "Content-Type": "application/json",
            }
        };

        axios.post('', formData, config)
            .then(() => {
                return axios.get("", config);
            })
            .then((response) => {
                setAnswers(prev => [...prev.slice(0, -1), { 
                    my: message, 
                    ai: response.data 
                }]);
            })
            .catch((err) => {
                setAnswers(prev => [...prev.slice(0, -1), { 
                    my: message, 
                    ai: "Произошла ошибка"
                }]);
                console.error(err);
            })
            .finally(() => {
                setLoading(false);
            });
    };
    return (
        <section className={style["chat"]}>
            <button
            className={style["logout"]}
                style={{ backgroundColor: "var(--magenta)", marginLeft: "40px" }}
                onClick={() => {dispatch({ type: LOGOUT })}}
            >Выйти
            </button>
            
            <div className={style["content"]} id="content">
                {answers.map((item, index) => (
                    <div key={index}>
                        <div className={style["my"]}>
                            <div className={style["message"]}><p>{item?.my}</p></div> 
                        </div>
                        <div className={style["ai"]}>
                            <div className={style["message"]}><p>{item.ai ? item.ai : (loading ? <Loader /> : item.ai)}</p></div>
                        </div>
                    </div>
                ))}
            </div>
            
            <div className={style["container"]}>
                <div className={style["flex"]}>
                    <textarea
                        placeholder="Введите запрос"
                        rows={1}
                        value={message}
                        onChange={handleChange}
                        className={style["input"]}
                        ref={textareaRef}
                    />
                    <button 
                        type="submit" 
                        onClick={handleSubmit}
                        disabled={loading || !message.trim()}
                    >
                        <img src={rightArrow} alt="Отправить" />
                    </button>
                </div>
            </div>
        </section>
    );
};