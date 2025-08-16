import React from "react";

const ProductPage = () => {
  return (
    <div className="w-full h-screen flex items-center justify-center">
      <iframe
        src="/streamlit/"
        className="w-full h-full border-none"
      />
    </div>
  );
};

export default ProductPage;