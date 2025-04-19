import { applyMiddleware, createStore } from "redux";
import { composeWithDevTools } from '@redux-devtools/extension';
import rootReducer from "./reducers";

function getInitialState() {
    return {
        auth: {
            isAuthenticated: localStorage.getItem("isAuthenticated") === "true",
        },
    };
}

const store = createStore(
    rootReducer,
    getInitialState(),
    composeWithDevTools(applyMiddleware()),
);

export default store;