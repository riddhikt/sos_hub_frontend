import React, { useState, useRef } from "react";
import { PhotoIcon } from "@heroicons/react/24/solid";
import EXIF from "exif-js";
import Overlay from "./Overlay";

function Form() {
  const initialState = {
    imageInfo: null,
    category: "",
    description: "",
  };
  const [formData, setFormData] = useState(initialState);
  const [imageMetadata, setImageMetadata] = useState(null);
  const [imagePreview, setImagePreview] = useState(null); // For storing the preview URL
  const [isLoading, setIsLoading] = useState(false);
  const [isOverlayOpen, setIsOverlayOpen] = useState(false);
  const [overlayLoading, setOverlayLoading] = useState(false);
  const [responseData, setResponseData] = useState({});

  const fileInputRef = useRef(null); // Add this line

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Generate a URL for the image preview
      setImagePreview(URL.createObjectURL(file));
      // Set the file object to formData
      setFormData((prevFormData) => ({
        ...prevFormData,
        imageInfo: file, // Store the file object
      }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsOverlayOpen(true); // Open the overlay when form submission starts
    setOverlayLoading(true);

    // Check if geolocation is available
    if (!navigator.geolocation) {
      console.error("Geolocation is not supported by this browser.");
      setIsLoading(false);
      return;
    }

    const convertToBase64 = (file) =>
      new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = (error) => reject(error);
      });

    // Attempt to convert image to Base64 (if exists)
    const imageBase64 = formData.imageInfo
      ? await convertToBase64(formData.imageInfo)
      : null;

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        // Construct the JSON payload
        const payload = {
          category: formData.category,
          description: formData.description,
          location: {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          },
          image_base64: imageBase64,
        };

        console.log(payload);

        // Send the JSON payload to your backend
        try {
          const response = await fetch("https://soshub-43a0b726d57f.herokuapp.com/analyze", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
          });

          if (!response.ok) {
            throw new Error("Network response was not ok");
          }

          const responseData = await response.json();
          console.log("Successfully submitted:", responseData);
          setResponseData(responseData);

          // Update the state or UI as necessary
        } catch (error) {
          console.error("Failed to submit form:", error);
          setResponseData({ message: "Submission failed. Please try again later." });
        } finally {
          setIsLoading(false);
        }
      },
      (error) => {
        console.error("Error Code = " + error.code + " - " + error.message);
        setIsLoading(false);
      }
    );
  };

  const handleReset = () => {
    console.log("calling reset")
    setFormData(initialState);
    setImagePreview(null)
  };

  return (
    <div className="mx-auto max-w-4xl p-8">
      <form onSubmit={handleSubmit}>
        {/* Image */}
        <div className="col-span-full">
          <label className="block text-sm font-medium leading-6 text-gray-900 text-left">
            Image
          </label>
          <div className="mt-2 flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10">
            <div className="text-center">
              {imagePreview ? (
                <>
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="max-w-xs h-auto"
                  />
                  <button
                    type="button"
                    onClick={() => setImagePreview(null)}
                    className="text-sm relative cursor-pointer rounded-md bg-white font-semibold text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 hover:text-indigo-500"
                  >
                    Change Image
                  </button>
                </>
              ) : (
                <>
                  <PhotoIcon
                    className="mx-auto h-12 w-12 text-gray-300"
                    aria-hidden="true"
                  />
                  <div className="mt-4 flex text-sm leading-6 text-gray-600">
                    <label className="relative cursor-pointer rounded-md bg-white font-semibold text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 hover:text-indigo-500">
                      <span>Upload an Image</span>
                      <input
                        id="imageInfo"
                        name="imageInfo"
                        type="file"
                        accept="image/png, image/jpeg, image/gif" // Specify accepted file formats
                        className="sr-only"
                        capture // This attribute is used to tell the browser to use camera for capturing an image
                        required
                        onChange={handleFileChange}
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                </>
              )}

              <p className="text-xs leading-5 text-gray-600">
                PNG, JPG, GIF up to 10MB
              </p>
            </div>
          </div>
        </div>

        {/* Dropdown */}
        <div className="mt-4 w-full">
          <label className="block text-sm font-medium leading-6 text-gray-900 text-left">
            Category
          </label>
          <div className="mt-2">
            <select
              id="category"
              name="category"
              autoComplete="country-name"
              className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              onChange={handleChange}
              value={formData.category}
            >
              <option></option>
              <option>Injury</option>
              <option>Accident</option>
              <option>Medical Emergency</option>
              <option>Fire</option>
              <option>Theft</option>
              <option>Breaking and Entering</option>
            </select>
          </div>
        </div>

        {/* Description */}
        <div className="mt-4 col-span-full">
          <label className="block text-sm font-medium leading-6 text-gray-900 text-left">
            Description
          </label>
          <div className="mt-2">
            <textarea
              id="description"
              name="description"
              rows={3}
              className="block w-full rounded-md border-0 p-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
              onChange={handleChange}
              value={formData.description}
            />
          </div>
        </div>

        {/* Submit and Reset */}
        <div className="mt-6 flex flex-col sm:flex-row sm:gap-x-4 gap-y-4">
          <button
            type="button"
            className="text-sm font-semibold leading-6 text-gray-900 bg-white border border-gray-300 rounded-md shadow-sm px-4 py-2 w-full transition duration-150 ease-in-out hover:bg-gray-50 focus:outline-none focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            onClick={handleReset}
          >
            Reset
          </button>
          <button
            type="submit"
            className="text-sm font-semibold leading-6 text-white bg-indigo-600 border border-transparent rounded-md shadow-sm px-4 py-2 w-full transition duration-150 ease-in-out hover:bg-indigo-500 focus:outline-none focus:border-indigo-700 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
          >
            Submit
          </button>
        </div>
      </form>

      {/* Displaying the location */}
      {/* {location && (
        <p className="text-xs leading-5 text-gray-600">
          Latitude: {location.latitude}, Longitude: {location.longitude}
        </p>
      )} */}
      
      <Overlay 
        open={isOverlayOpen}
        setOpen={setIsOverlayOpen}
        isLoading={isLoading}
        responseData={responseData}
      />

      <p className="mt-10 text-xs font-medium leading-6 text-gray-500">
        Made with ❤️ for SF
      </p>
    </div>
  );
}

export default Form;
