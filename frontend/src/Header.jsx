import {Link, NavLink} from "react-router-dom";

function Header() {
    return (
        <header className={"relative top-0 left-0 w-full z-50 bg-gray-700 py-6 px-10"}>
            <nav className={"flex flex-row items-center justify-start gap-10 text-4xl font-bold leading-tight"}>
                <Link to="/" className={"text-blue-300"}>
                    CNC-Whiteboard
                </Link>

                <ul className={"flex flex-row gap-10 text-blue-200"}>
                    <li>
                        <NavLink to="/images"
                                 className={({isActive}) => isActive ? "text-blue-300" : "hover:text-blue-300 duration-700"}>
                            Images
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/svgs"
                                 className={({isActive}) => isActive ? "text-blue-300" : "hover:text-blue-300 duration-700"}>
                            SVGs
                        </NavLink>
                    </li>
                </ul>
            </nav>
        </header>
    )
}

export default Header;