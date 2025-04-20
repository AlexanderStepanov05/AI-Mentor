import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import style from "./NavBar.module.css";
import chat from "../../assets/chat.svg"
import home from "../../assets/home.svg"

export default function NavBar() {
    const location = useLocation();
    const [activePath, setActivePath] = useState(location.pathname);
    const [windowSize, setWindowSize] = useState({
        width: window.innerWidth,
        height: window.innerHeight
    });

    useEffect(() => {
        const handleResize = () => {
            setWindowSize({
                width: window.innerWidth,
                height: window.innerHeight
            });
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        setActivePath(location.pathname);
    }, [location]);

    useEffect(() => {
        const navbar = document.getElementById("navbar"); 
        const ul = document.getElementById("ul");
        
        if (!navbar || !ul) return;

        if (location.pathname === "/main") {
            if (windowSize.width < 450) {
                ul.style.flexDirection = "column";
                navbar.style.left = "25px";
                navbar.style.top = "50%";
                navbar.style.transform = "translateY(-50%)";
            } else if (windowSize.width > 450) {
                ul.style.flexDirection = "column";
                navbar.style.left = "25px";
                navbar.style.top = "50%";
                navbar.style.transform = "translateY(-50%)";
            }
        } else if (location.pathname === "/main/page") {
            if (windowSize.width < 450) {
                ul.style.flexDirection = "row";
                navbar.style.left = "50%";
                navbar.style.top = "90%";
                navbar.style.transform = "translateX(-50%)"; 
            } else if (windowSize.width > 450) {
                ul.style.flexDirection = "column";
                navbar.style.left = "25px";
                navbar.style.top = "50%";
                navbar.style.transform = "translateY(-50%)";
            }
        }
    }, [windowSize.width])
    return (
        <nav className={style["nav-bar"]} id='navbar'>
            <ul id='ul'>
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