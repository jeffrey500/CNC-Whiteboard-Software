import upload from "./assets/upload.svg";
import {useState, useEffect} from "react";

function Images() {
    // variables for handling image upload
    const [image, setImage] = useState(null);
    const [isUploading, setIsUploading] = useState(false);

    // variables for handling the image sidebar preview
    const [storedImages, setStoredImages] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [refreshImages, setRefreshImages] = useState(0);

    // tracks selected image
    const [selectedImage, setSelectedImage] = useState(-1);

    // tracks image preview for main screen
    const [preview, setPreview] = useState(null);

    // tracks status of plotting
    const [plot, setPlot] = useState(false);
    const [port, setPort] = useState("Type Port...");
    const [plotting, setPlotting] = useState(false);

    // fetches the stored images from the backend during initial loading and upon refresh
    useEffect(() => {
        const fetchImages = async () => {
            setIsLoading(true);
            try {
                const response = await fetch('http://192.168.2.179:5050/image/');
                if (response.ok) {
                    const data = await response.json();
                    setStoredImages(data);
                } else {
                    console.error('Failed to fetch images:', response.statusText);
                }
            } catch (error) {
                console.error('Error fetching images:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchImages();
    }, [refreshImages]);

    // handles the image sidebar preview refresh
    const handleRefresh = () => {
        setRefreshImages(prevCount => prevCount + 1);
    };

    // handles image preview after uploading
    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImage(file);
            setPreview(URL.createObjectURL(file));
        }
    };

    // handles api call after image upload
    const handleUpload = async () => {
        if (!image) {
            alert('Please select an image first!');
            return;
        }

        setIsUploading(true);

        const formData = new FormData();
        formData.append('file', image);

        try {
            const response = await fetch('http://192.168.2.179:5050/image/', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                alert('Upload successful!');
                setImage(null);
                setPreview(null);
                handleRefresh();
            } else {
                alert('Upload failed.');
            }
        } catch (error) {
            console.error('Error uploading image:', error);
        } finally {
            setIsUploading(false);
        }
    };

    // handles selecting an image from the sidebar
    const selectImage = (index) => {
        setSelectedImage(index);
    }

    // handles deleting selected image
    const deleteImage = async () => {
        try {
            const response = await fetch(`http://192.168.2.179:5050/image/${storedImages[selectedImage].id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                alert('Image deleted successfully!');
                handleRefresh();
                setSelectedImage(-1);
            } else {
                alert('Failed to delete image.');
            }
        } catch (error) {
            console.error('Error deleting image:', error);
        }
    }

    // handles plotting selected image
    const plot_image = async () => {
        try {
            setPlotting(true);

            const response = await fetch(`http://192.168.2.179:5050/image/plot/${storedImages[selectedImage].id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    port: port
                }),
            });

            if (response.ok) {
                alert('Image plotted!');
            } else {
                alert('Failed to plot image.');
            }
        } catch (error) {
            console.error('Error plotting image:', error);
        }
        setPlotting(false);
    }

    // handles getting the render filepath
    function getRenderPath(filename) {
        return filename.substring(0, filename.lastIndexOf('.')) + '.png'
    }


    return (
        // left preview column
        <div className={"grid grid-cols-[2fr_5fr] gap-2 w-full h-full justify-center items-center"}>
            <div className={"flex flex-col overflow-y-auto py-8 h-full w-full items-center"}>

                {/*handles the conditional loading of the stored preview images*/}
                {isLoading ? (
                    <div className={"text-gray-500 font-bold text-center py-10"}>Loading...</div>
                ) : storedImages.length === 0 ? (
                    <div className={"text-gray-500 font-bold text-center py-10"}>No Stored Images</div>
                ) : (
                    <div className={"flex flex-col max-w-2/3 gap-10"}>
                        <h1 className={"text-5xl font-bold text-gray-500 py-2 text-center"}>Stored Images</h1>
                        {storedImages.map((img, index) => (
                            <div>
                                <div className={"cursor-pointer"}
                                     key={index}
                                     onClick={() => selectImage(index)}
                                >
                                    <img
                                        src={`http://192.168.2.179:5050/static/image_inputs/${img.name}`}
                                        alt={img.name}
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
                {selectedImage !== -1 ? (

                    //*display selected image*
                    <div className={"flex flex-col relative w-full items-center gap-8 max-w-2/3 py-10"}>

                        <h1 className={"text-5xl font-bold text-gray-500 w-full text-left"}>{storedImages[selectedImage].name}</h1>

                        {/*displays the selected image*/}
                        <img src={`http://192.168.2.179:5050/static/image_inputs/${storedImages[selectedImage].name}`}
                             alt={storedImages[selectedImage].name}
                             className="max-w-full object-contain border-3 border-gray-500"/>

                        <h1 className={"text-5xl font-bold text-gray-500 w-full text-left"}>Plotting Render</h1>

                        {/*displays the image plotting render*/}
                        <img src={`http://192.168.2.179:5050/static/image_render/${getRenderPath(storedImages[selectedImage].name)}`}
                             alt={getRenderPath(storedImages[selectedImage].name)}
                             className="max-w-full object-contain border-3 border-gray-500"/>

                        {plotting ? (
                            <div className={"flex flex-col gap-4 pt-6 items-center justify-center w-full pb-10"}>
                                <h1 className={"text-3xl font-bold text-gray-500 w-full text-center"}>Plotting...</h1>
                            </div>
                        ) : plot ? (
                            <div className={"flex flex-row gap-4 pt-6 items-center justify-center w-full"}>
                                <button
                                    onClick={() => plot_image()}
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
                                    onClick={() => setPlot(true)}
                                    className="py-4 px-6 rounded-lg border-2 cursor-pointer border-green-400 bg-green-200 text-gray-600 hover:bg-green-300 duration-300"
                                >
                                    Plot
                                </button>

                                <button
                                    onClick={() => deleteImage()}
                                    className="py-4 px-6 rounded-lg border-2 cursor-pointer border-red-400 bg-red-200 text-gray-600 hover:bg-red-300 duration-300"
                                >
                                    Delete Image
                                </button>

                                <button
                                    onClick={() => setSelectedImage(-1) }
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
                                    setImage(null);
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
                            htmlFor="image-upload">
                            <img src={upload} className="h-30 w-30" alt="upload-image"/>
                            <h1 className={"text-4xl font-bold text-gray-400 py-5"}>Upload Image</h1>
                            <input type="file" id="image-upload" accept="image/*" onChange={handleImageChange}
                                   className={"hidden"}/>
                        </label>
                    </div>
                )}
            </div>
        </div>
    )
}

export default Images;