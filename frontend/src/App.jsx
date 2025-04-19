import { Provider } from "react-redux";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import "./static/App.css";
import store from "./store.jsx";

import Reg  from "./components/Registration/Reg.jsx"
import Login  from "./components/Login/Login.jsx";
import Layout from "./components/Layout.jsx";
import {MainChat} from "./components/MainChat/MainChat.jsx";
import { About } from "./components/About/About.jsx";

const router = createBrowserRouter([
    {
        path: "/main",
        element: <Layout />,
        children: [
            {
                path: "/main",
                element: <MainChat />,
            },
            {
                path: "/main/page",
                element: <About />,
            },
        ],
    },
    {
        path: "/",
        element: <Login />,
    },
    {
        path: "/reg",
        element: <Reg />,
    },
]);

function App() {
    return (
        <>
            <Provider store={store}>
                <RouterProvider router={router}></RouterProvider>
            </Provider>
        </>
    );
}

export default App;