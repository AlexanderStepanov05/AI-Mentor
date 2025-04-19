import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import style from "./NavBar.module.css";
import chat from "../../assets/chat.svg"
import home from "../../assets/home.svg"

export default function NavBar() {
    const location = useLocation();
    const [activePath, setActivePath] = useState(location.pathname);

    useEffect(() => {
        setActivePath(location.pathname);
    }, [location]); 
    return (
        <nav className={style["nav-bar"]}>
            <ul>
                <li
                    className={
                        activePath === "/main/page" ? style.active : ""
                    }
                >
                    <Link to="/main/page" >
                        <img src={chat} alt="Лендинг" />
                    </Link>
                </li>
                <li className={activePath === "/main" ? style.active : ""}>
                    <Link to="/main">
                        <img src={home} alt="Чат" />
                    </Link>
                </li>
            </ul>
        </nav>
    );
}