import {Routes, Route} from "react-router-dom";
import Header from "./Header.jsx";
import Images from "./Images.jsx";
import SVGs from "./SVGs.jsx";
import Home from "./Home.jsx";

function App() {
    return (
        <div className={"w-full h-screen flex flex-col overflow-hidden"}>
            <Header/>
            <div className={"flex-1 min-h-0"}>
                <Routes>
                    <Route path={"/"} element={<Home/>}/>
                    <Route path={"/svgs"} element={<SVGs/>}/>
                    <Route path={"/images"} element={<Images/>}/>
                </Routes>
            </div>
        </div>
    )
}

export default App;