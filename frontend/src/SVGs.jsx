import upload from "./assets/upload.SVG";
import {useState, useEffect} from "react";

function SVGs() {
    // variables for handling SVG upload
    const [SVG, setSVG] = useState(null);
    const [isUploading, setIsUploading] = useState(false);

    // variables for handling the SVG sidebar preview
    const [storedSVGs, setStoredSVGs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [refreshSVGs, setRefreshSVGs] = useState(0);

    // tracks selected SVG
    const [selectedSVG, setSelectedSVG] = useState(-1);

    // tracks SVG preview for main screen
    const [preview, setPreview] = useState(null);

    // tracks re-transform of the SVG
    const [reTransform, setReTransform] = useState(false);
    const [num1, setNum1] = useState(1);
    const [num2, setNum2] = useState(0);
    const [num3, setNum3] = useState(1);
    const [num4, setNum4] = useState(0);

    // tracks status of plotting
    const [plot, setPlot] = useState(false);
    const [port, setPort] = useState("Type Port...");
    const [plotting, setPlotting] = useState(false);

    // fetches the stored SVGs from the backend during initial loading and upon refresh
    useEffect(() => {
        const fetchSVGs = async () => {
            setIsLoading(true);
            try {
                const response = await fetch('http://192.168.2.179:5050/svg/');
                if (response.ok) {
                    const data = await response.json();
                    setStoredSVGs(data);
                } else {
                    console.error('Failed to fetch SVGs:', response.statusText);
                }
            } catch (error) {
                console.error('Error fetching SVGs:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchSVGs();
    }, [refreshSVGs]);

    // handles the SVG sidebar preview refresh
    const handleRefresh = () => {
        setRefreshSVGs(prevCount => prevCount + 1);
    };

    // handles SVG preview after uploading
    const handleSVGChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSVG(file);
            setPreview(URL.createObjectURL(file));
        }
    };

    // handles api call after SVG upload
    const handleUpload = async () => {
        if (!SVG) {
            alert('Please select an SVG first!');
            return;
        }

        setIsUploading(true);

        const formData = new FormData();
        formData.append('file', SVG);

        try {
            const response = await fetch('http://192.168.2.179:5050/svg/', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                alert('Upload successful!');
                setSVG(null);
                setPreview(null);
                handleRefresh();
            } else {
                alert('Upload failed.');
            }
        } catch (error) {
            console.error('Error uploading SVG:', error);
        } finally {
            setIsUploading(false);
        }
    };

    // handles selecting an SVG from the sidebar
    const selectSVG = (index) => {
        setSelectedSVG(index);
    }

    // handles deleting selected SVG
    const deleteSVG = async () => {
        try {
            const response = await fetch(`http://192.168.2.179:5050/svg/${storedSVGs[selectedSVG].id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                alert('SVG deleted successfully!');
                handleRefresh();
                setSelectedSVG(-1);
            } else {
                alert('Failed to delete SVG.');
            }
        } catch (error) {
            console.error('Error deleting SVG:', error);
        }
    }

    // handles getting the render filepath
    function getRenderPath(filename) {
        return filename.substring(0, filename.lastIndexOf('.')) + '.png'
    }

    // handles plotting selected SVG
    const plot_svg = async () => {
        try {
            setPlotting(true);

            const response = await fetch(`http://192.168.2.179:5050/svg/plot/${storedSVGs[selectedSVG].id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    port: port
                }),
            });

            if (response.ok) {
                alert('SVG plotted!');
            } else {
                alert('Failed to plot svg.');
            }
        } catch (error) {
            console.error('Error plotting svg:', error);
        }
        setPlotting(false);
    }

    const transform = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch(`http://192.168.2.179:5050/svg/${storedSVGs[selectedSVG].id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    x_scale: parseFloat(num1),
                    x_translate: parseFloat(num2),
                    y_scale: parseFloat(num3),
                    y_translate: parseFloat(num4)
                }),
            });
            if (response.ok) {
                alert('Re-Transform successful!');
                setReTransform(false);
                handleRefresh();
            } else {
                alert('Re-Transform failed.');
            }
        } catch (error) {
            console.error('Error re-transforming SVG:', error);
        }
    }

    return (
        // left preview column
        <div className={"grid grid-cols-[2fr_5fr] gap-2 w-full h-full justify-center items-center"}>
            <div className={"flex flex-col overflow-y-auto py-8 h-full w-full items-center"}>

                {/*handles the conditional loading of the stored preview SVGs*/}
                {isLoading ? (
                    <div className={"text-gray-500 font-bold text-center py-10"}>Loading...</div>
                ) : storedSVGs.length === 0 ? (
                    <div className={"text-gray-500 font-bold text-center py-10"}>No Stored SVGs</div>
                ) : (
                    <div className={"flex flex-col max-w-2/3 gap-10"}>
                        <h1 className={"text-5xl font-bold text-gray-500 py-2 text-center"}>Stored SVGs</h1>
                        {storedSVGs.map((svg, index) => (
                            <div>
                                <div className={"cursor-pointer"}
                                     key={index}
                                     onClick={() => selectSVG(index)}
                                >
                                    <img
                                        src={`http://192.168.2.179:5050/static/SVG_inputs/${svg.name}`}
                                        alt={svg.name}
                                        className={"max-w-full max-h-full object-contain border-3 border-gray-500"}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/*center display*/}
            <div className={"flex flex-col items-center w-full h-full overflow-y-auto"}>
                {selectedSVG !== -1 ? (

                    //*display selected SVG*
                    <div className={"flex flex-col relative w-full items-center gap-8 max-w-2/3 py-10"}>

                        <h1 className={"text-5xl font-bold text-gray-500 w-full text-left"}>{storedSVGs[selectedSVG].name}</h1>

                        {/*displays the selected SVG*/}
                        <img src={`http://192.168.2.179:5050/static/SVG_inputs/${storedSVGs[selectedSVG].name}`}
                             alt={storedSVGs[selectedSVG].name}
                             className="max-w-full object-contain border-3 border-gray-500"/>

                        <h1 className={"text-5xl font-bold text-gray-500 w-full text-left"}>Plotting Render</h1>

                        {/*displays the SVG plotting render*/}
                        <img src={`http://192.168.2.179:5050/static/SVG_render/${getRenderPath(storedSVGs[selectedSVG].name)}?t=${refreshSVGs}`}
                             alt={getRenderPath(storedSVGs[selectedSVG].name)}
                             className="max-w-full object-contain border-3 border-gray-500"/>

                        { reTransform ? (
                            <div className={"flex flex-col items-center justify-center w-full"}>
                                <h1 className={"text-5xl font-bold text-gray-500"}>Re-Transform</h1>

                                <div className={"flex flex-row gap-4 pt-8"}>
                                    <form onSubmit={transform} className="flex flex-col gap-6">
                                        <div className="flex flex-row gap-4">
                                            <label className="flex flex-col w-full text-gray-400 font-bold uppercase tracking-wider text-sm gap-2">
                                                X-Scale Factor
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    value={num1}
                                                    onChange={(e) => setNum1(e.target.value)}
                                                    required
                                                    className="p-3 border-2 border-gray-300 rounded-xl text-gray-600 font-normal focus:outline-none transition-colors bg-white"
                                                />
                                            </label>

                                            <label className="flex flex-col w-full text-gray-400 font-bold uppercase tracking-wider text-sm gap-2">
                                                X-Translate
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    value={num2}
                                                    onChange={(e) => setNum2(e.target.value)}
                                                    required
                                                    className="p-3 border-2 border-gray-300 rounded-xl text-gray-600 font-normal focus:outline-none transition-colors bg-white"
                                                />
                                            </label>
                                        </div>
                                        <div className="flex flex-row gap-4">
                                            <label className="flex flex-col w-full text-gray-400 font-bold uppercase tracking-wider text-sm gap-2">
                                                Y-Scale Factor
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    value={num3}
                                                    onChange={(e) => setNum3(e.target.value)}
                                                    required
                                                    className="p-3 border-2 border-gray-300 rounded-xl text-gray-600 font-normal focus:outline-none transition-colors bg-white"
                                                />
                                            </label>

                                            <label className="flex flex-col w-full text-gray-400 font-bold uppercase tracking-wider text-sm gap-2">
                                                Y-Translate
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    value={num4}
                                                    onChange={(e) => setNum4(e.target.value)}
                                                    required
                                                    className="p-3 border-2 border-gray-300 rounded-xl text-gray-600 font-normal focus:outline-none transition-colors bg-white"
                                                />
                                            </label>
                                        </div>

                                        <div className="flex flex-row gap-4 pt-2 w-full">
                                            <button
                                                type="submit"
                                                className="w-full py-3 rounded-xl border-2 cursor-pointer font-bold border-orange-400 bg-orange-200 text-gray-600 hover:bg-orange-300 transition-colors duration-300"
                                            >
                                                Submit
                                            </button>

                                            <button
                                                type="button"
                                                onClick={() => setReTransform(false)}
                                                className="w-full py-3 rounded-xl border-2 cursor-pointer font-bold border-gray-300 bg-white text-gray-600 hover:bg-gray-200 transition-colors duration-300"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>

                        ) : plotting ? (
                            <div className={"flex flex-col gap-4 pt-6 items-center justify-center w-full pb-10"}>
                                <h1 className={"text-3xl font-bold text-gray-500 w-full text-center"}>Plotting...</h1>
                            </div>
                        ): plot ? (
                            <div className={"flex flex-row gap-4 pt-6 items-center justify-center w-full"}>
                                <button
                                    onClick={() => plot_svg()}
                                    className="py-4 px-6 rounded-lg border-2 cursor-pointer border-green-400 bg-green-200 text-gray-600 hover:bg-green-300 duration-300"
                                >
                                    Send G-code
                                </button>

                                <label className="flex flex-col w-55 text-gray-400 font-bold uppercase tracking-wider text-sm gap-2">
                                    <input
                                        type="text"
                                        value={port}
                                        onChange={(e) => setPort(e.target.value)}
                                        required
                                        className="py-4 px-6 border-2 border-orange-400 rounded-lg text-gray-600 font-normal focus:outline-none transition-colors bg-orange-100 w-full"
                                    />
                                </label>

                                <button
                                    onClick={() => setPlot(false) }
                                    className="py-4 px-6 rounded-lg border-2 cursor-pointer border-gray-300 text-gray-600 hover:bg-gray-200 duration-300"
                                >
                                    Cancel
                                </button>
                            </div>
                        ) : (
                            <div className={"flex flex-row gap-4 pt-6"}>
                                 <button
                                    onClick={() => {setPlot(true)}}
                                    className="py-4 px-6 rounded-lg border-2 cursor-pointer border-green-400 bg-green-200 text-gray-600 hover:bg-green-300 duration-300"
                            >
                                Plot Gcode
                            </button>

                            <button
                                onClick={() => {setReTransform(true)}}
                                className="py-4 px-6 rounded-lg border-2 cursor-pointer border-orange-400 bg-orange-200 text-gray-600 hover:bg-orange-300 duration-300"
                            >
                                Re-Transform
                            </button>

                            <button
                                onClick={() => deleteSVG()}
                                className="py-4 px-6 rounded-lg border-2 cursor-pointer border-red-400 bg-red-200 text-gray-600 hover:bg-red-300 duration-300"
                            >
                                Delete SVG
                            </button>

                            <button
                                onClick={() => setSelectedSVG(-1) }
                                className="py-4 px-6 rounded-lg border-2 cursor-pointer border-gray-300 text-gray-600 hover:bg-gray-200 duration-300"
                            >
                                Cancel
                            </button>
                        </div>
                        )}
                    </div>

                    // display upload preview
                ) : preview ? (
                    <div className={"flex flex-col relative w-full h-full justify-center items-center"}>
                        <img src={preview} alt="preview" className="max-w-[70vw] max-h-[60vh] object-contain border-3 border-gray-500"/>
                        <div className={"flex flex-row gap-4 pt-6"}>
                            <button
                                onClick={handleUpload}
                                disabled={isUploading}
                                className="py-4 px-6 cursor-pointer rounded-lg bg-blue-200 border-2 border-blue-300 text-gray-600 hover:bg-blue-300 disabled:opacity-50 duration-300"
                            >
                                {isUploading ? 'Uploading...' : 'Confirm Upload'}
                            </button>

                            <button
                                onClick={() => {
                                    setPreview(null);
                                    setSVG(null);
                                }}
                                className="py-4 px-6 cursor-pointer rounded-lg border-2 border-gray-300 text-gray-600 hover:bg-gray-200 duration-300"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>

                    // display upload button
                ) : (
                    <div className={"flex flex-col relative w-full h-full justify-center items-center"}>
                        <label
                            className={"flex flex-col items-center justify-center cursor-pointer rounded-3xl border-4 border-gray-400 bg-gray-100 hover:bg-gray-200 w-1/3 h-1/3"}
                            htmlFor="SVG-upload">
                            <img src={upload} className="h-30 w-30" alt="upload-SVG"/>
                            <h1 className={"text-4xl font-bold text-gray-400 py-5"}>Upload SVG</h1>
                            <input type="file" id="SVG-upload" accept=".svg, image/svg+xml" onChange={handleSVGChange}
                                   className={"hidden"}/>
                        </label>
                    </div>
                )}
            </div>
        </div>
    )
}

export default SVGs;