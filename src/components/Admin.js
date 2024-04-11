import React, { useState, useEffect } from "react";
import Navbar from "./Navbar";

function Admin() {
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true); // Start loading indicator
      try {
        const response = await fetch(
          "https://soshub-43a0b726d57f.herokuapp.com/get_db"
        );
        const jsonData = await response.json();
        setData(jsonData.data);
        console.log(jsonData.data);
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false); // End loading indicator
      }
    };

    fetchData();
  }, []);

  return (
    <>
      <Navbar />
      <div className="flex flex-col max-w-4xl mx-auto overflow-hidden shadow-md my-5">
        {isLoading ? (
          <div className="flex justify-center items-center min-h-screen">
            <div
              className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full"
              role="status"
            >
              <span className="visually-hidden"></span>
            </div>
          </div>
        ) : (
          <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
              <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="w-1/7 whitespace-normal px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Severity
                      </th>
                      <th
                        scope="col"
                        className="w-2/7 whitespace-normal px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Emergency
                      </th>
                      <th
                        scope="col"
                        className="w-1/7 whitespace-normal px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Responders
                      </th>
                      <th
                        scope="col"
                        className="w-1/7 whitespace-normal px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Location
                      </th>
                      <th
                        scope="col"
                        className="w-1/7 whitespace-normal px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Confidence
                      </th>
                      <th
                        scope="col"
                        className="w-1/7 whitespace-normal px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Date and Time
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {data.map((item, index) => (
                      <tr key={index} className="hover:bg-gray-100">
                        <td className="px-6 py-4 whitespace-normal text-sm text-gray-800">
                          {item.llama_analysis.severity}
                        </td>
                        <td className="px-6 py-4 whitespace-normal text-sm text-gray-800">
                          {item.llama_analysis.emergency}
                        </td>
                        <td className="px-6 py-4 whitespace-normal text-sm text-gray-800">
                          {item.llama_analysis.responders.join(", ")}
                        </td>
                        <td className="px-6 py-4 whitespace-normal text-sm text-gray-800">
                          {`Latitude: ${item.location.latitude}, Longitude: ${item.location.longitude}`}
                        </td>
                        <td className="px-6 py-4 whitespace-normal text-sm text-gray-800">
                          {item.llama_analysis.confidence}
                        </td>
                        <td className="px-6 py-4 whitespace-normal text-sm text-gray-800">
                          {item.datetime}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default Admin;
