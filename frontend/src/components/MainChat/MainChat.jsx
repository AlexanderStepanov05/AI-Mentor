import { useState, useRef, useEffect } from "react";
import style from "./MainChat.module.css";
import rightArrow from "../../assets/rightArrow.svg";
import axios from "axios";
import Loader from "../Loader/Loader";

export const MainChat = () => {
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const textareaRef = useRef(null);
    const [answers, setAnswers] = useState([]);

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
        
        const config = {
            headers: {
                "Content-Type": "application/json",
                "Authorization": "", 
            }
        };

        axios.post('', formData, config)
            .then(() => {
                return axios.get("", config);
            })
            .then((response) => {
                setAnswers(prev => [...prev, { 
                    my: message, 
                    ai: response.data 
                }]);
            })
            .catch((err) => {
                setAnswers(prev => [...prev, { 
                    my: message, 
                }]);
                console.error(err);
            })
            .finally(() => {
                setLoading(false);
            });
    };
    return (
        <section className={style["chat"]}>
            <div className={style["content"]}>
                {answers.map((item, index) => (
                    <div key={index}>
                        <div className={style["my"]}>
                            <div className={style["message"]}><p>{item?.my}</p></div> 
                        </div>
                        <div className={style["ai"]}>
                            <div className={style["message"]}><p>{item.ia ? item?.ai : "Произошла ошибка"}</p></div>
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
                        {loading ? <Loader /> : <img src={rightArrow} alt="Отправить" />}
                    </button>
                </div>
            </div>
        </section>
    );
};