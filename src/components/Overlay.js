// Overlay.js
import React, { Fragment } from "react";
import { Dialog, Transition } from "@headlessui/react";

const Overlay = ({ open, setOpen, isLoading, responseData }) => {
  const emergencyAnalysis =
    responseData?.[0]?.llama_analysis?.emergency || "Loading analysis...";
  const dos = responseData?.[0]?.recommendations?.dos || [];
  const donts = responseData?.[0]?.recommendations?.donts || [];

  return (
    <Transition.Root show={open} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={() => setOpen(false)}>
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
                <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  {isLoading ? (
                    <div className="flex justify-center items-center p-12">
                      <div
                        className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full"
                        role="status"
                      >
                        <span className="visually-hidden">Loading...</span>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="text-lg leading-6 font-medium text-gray-900">
                        Emergency Request Sent!
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-gray-500">
                          {emergencyAnalysis}
                        </p>
                      </div>
                      {dos.length > 0 && (
                        <div className="mt-4">
                          <h4 className="font-semibold">Dos:</h4>
                          <ul className="list-disc pl-5 space-y-1">
                            {dos.map((item, index) => (
                              <li key={index} className="text-sm text-gray-500">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {donts.length > 0 && (
                        <div className="mt-4">
                          <h4 className="font-semibold">Donts:</h4>
                          <ul className="list-disc pl-5 space-y-1">
                            {donts.map((item, index) => (
                              <li key={index} className="text-sm text-gray-500">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  )}
                </div>
                <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                  <button
                    type="button"
                    className="mt-3 w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                    onClick={() => setOpen(false)}
                  >
                    Close
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
};

export default Overlay;
