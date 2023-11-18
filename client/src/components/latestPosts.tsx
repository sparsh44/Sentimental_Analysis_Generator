import React, { useState, useEffect } from "react";
import Card from "../components/card";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import regional from "../../public/data/regional.json";
import sampleText from "../../public/data/sampleText.json";
import natural from 'natural';

import { Dropdown } from 'flowbite-react';


const latestPosts = () => {
  const regionalNews = sampleText.News;
  const [currentNumber, setNumber] = useState(0);
  const [newsData, setNewsData] = useState(regionalNews);
  const [currentSemantic, setCurrentSemantic] = useState("ALL");
  const [currActiveButton, setActiveButton] = useState("ALL");
  const [search, setSearch] = useState("");
  const [bookMark, setBookMark] = useState(false);
  const [bookMarkArr, setBookMarkArr] = useState([]);

  var currentNews = regionalNews;
  if (bookMark) {
  } else if (currentSemantic === "ALL") {
    currentNews = regionalNews;
    if (search != "") {
      currentNews = regionalNews.filter(function (d) {
        const lowerCaseQuery = search.toLowerCase();
        return (
          d["Title"].toLowerCase().includes(lowerCaseQuery) ||
          d["Description"].toLowerCase().includes(lowerCaseQuery)
        );
      });
    }
  } else {
    var allNews = regionalNews;
    if (search != "") {
      allNews = regionalNews.filter(function (d) {
        const lowerCaseQuery = search.toLowerCase();
        return (
          d["Title"].toLowerCase().includes(lowerCaseQuery) ||
          d["Description"].toLowerCase().includes(lowerCaseQuery)
        );
      });
    }
    var currName = currentSemantic;
    // console.log(currName);
    currentNews = allNews.filter(function (d) {
      const positive =
        100 -
        Math.round(parseFloat(d["Sentiment_Score"].split(" ")[1]) * 100) -
        Math.round(parseFloat(d["Sentiment_Score"].split(" ")[2]) * 100);
      const negative = Math.round(
        parseFloat(d["Sentiment_Score"].split(" ")[1]) * 100
      );
      const neutral = 100 - positive - negative;
      if (currentSemantic == "Positive") {
        return positive >= currentNumber;
      } else if (currentSemantic == "Negative") {
        return negative >= currentNumber;
      } else {
        return neutral >= currentNumber;
      }
    });
  }
  const handleSearch = (e: any) => {
    setSearch("")
    setCurrentSemantic(e);
  };
  const apiUrl = "http://127.0.0.1:8000/";
  useEffect(() => {
    // Fetch data from the API
    fetch(apiUrl)
      .then((response) => response.json())
      .then((data) => {
        setNewsData(data["News"]);
        for (let i = 0; i < data["News"].length; i++) {
          const negative = parseFloat(
            data["News"][i]["Sentiment_Score"].split(" ")[1]
          );
          if (negative >= 0.5) {
            fetch("https://email-kcr3.onrender.com/sendEmail", {
              // Adding method type
              method: "POST",

              // Adding body or contents to send
              body: JSON.stringify({
                title: data["News"][i]["Title"],
                url: data["News"][i]["URL"],
              }),

              // Adding headers to the request
              headers: {
                "Content-type": "application/json; charset=UTF-8",
              },
            })
              // Converting to JSON
              .then((response) => response.json())

              // Displaying results to console
              .then((json) => console.log(json));
          }
        }
      })
      .catch((error) => console.error("Error fetching data: ", error));
  }, []); // The empty array means this effect runs once after initial render


  const topKeywords = ['earthquake','crime', 'robbery', 'theft', 'assault', 'burglary', 'arson', 'fraud', 'kidnapping', 'homicide', 'violence' ,'other']
  return (
    <>
      <div className="mb-10">
        <div className="flex justify-center items-center text-5xl m-6 mt-12">
          LATEST ARTICLES
        </div>
        <div className="flex justify-center items-center">
          <div className="flex justify-center items-center ">
            <input
              onChange={(e) => {
                setSearch(e.target.value);
              }}
              style={{ width: 400, height: 50 }}
              type="text"
              className="input-text"
              placeholder="Search Keywords..."
            />
            <FontAwesomeIcon
              className="-ml-7 mt-1 hover:cursor-pointer"
              icon={faMagnifyingGlass}
            />
        <Dropdown label="Top Keywords" dismissOnClick={false} className="bg-black font-black">
            {topKeywords.map((keyword, index) => (
              <Dropdown.Item key={index} onClick={()=>setSearch(keyword)}>{keyword}</Dropdown.Item>
            ))}
          </Dropdown>
          </div>
          <div className="flex justify-center items-center space-x-4 ml-20">
            <p>Sort News By - </p>
            {currActiveButton == "ALL" ? (
              <button
                onClick={() => {
                  handleSearch("ALL");
                }}
                className="border-2 border-white bg-slate-200 text-black p-2 rounded-lg hover:scale-[1.05] duration-300 px-4"
              >
                ALL NEWS
              </button>
            ) : (
              <button
                onClick={() => {
                  handleSearch("ALL");
                  setActiveButton("ALL");
                }}
                className="border-2 p-2 rounded-lg hover:scale-[1.05] duration-300 hover:underline px-4 hover:bg-slate-200 hover:text-black"
              >
                ALL NEWS
              </button>
            )}
            {currActiveButton == "Positive" ? (
              <button
                onClick={() => {
                  handleSearch("Positive");
                }}
                className="border-2 border-white bg-slate-200 text-black p-2 rounded-lg hover:scale-[1.05] duration-300 px-4"
              >
                Positive
              </button>
            ) : (
              <button
                onClick={() => {
                  handleSearch("Positive");
                  setActiveButton("Positive");
                }}
                className="border-2 p-2 rounded-lg hover:scale-[1.05] duration-300 hover:underline px-4 hover:bg-slate-200 hover:text-black"
              >
                Positive
              </button>
            )}
            {currActiveButton == "Negative" ? (
              <button
                onClick={() => {
                  handleSearch("Negative");
                }}
                className="border-2 border-white bg-slate-200 text-black p-2 rounded-lg hover:scale-[1.05] duration-300 px-4"
              >
                Negative
              </button>
            ) : (
              <button
                onClick={() => {
                  handleSearch("Negative");
                  setActiveButton("Negative");
                }}
                className="border-2 p-2 rounded-lg hover:scale-[1.05] duration-300 hover:underline px-4 hover:bg-slate-200 hover:text-black"
              >
                Negative
              </button>
            )}
            {currActiveButton == "Neutral" ? (
              <button
                onClick={() => {
                  handleSearch("Neutral");
                }}
                className="border-2 border-white bg-slate-200 text-black p-2 rounded-lg hover:scale-[1.05] duration-300 px-4"
              >
                Neutral
              </button>
            ) : (
              <button
                onClick={() => {
                  handleSearch("Neutral");
                  setActiveButton("Neutral");
                }}
                className="border-2 p-2 rounded-lg hover:scale-[1.05] duration-300 hover:underline px-4 hover:bg-slate-200 hover:text-black"
              >
                Neutral
              </button>
            )}
            <input
              onChange={(e: any) => {
                setNumber(e.target.value);
              }}
              type="number"
              className="input-number border-2 p-2 rounded-lg"
              placeholder="Min %"
            />
            {!bookMark ? (
              <img
                className="hover:cursor-pointer"
                onClick={() => setBookMark(!bookMark)}
                src="Bookmark.png"
                width={70}
                height={70}
                alt=""
              />
            ) : (
              <img
                className="hover:cursor-pointer "
                onClick={() => setBookMark(!bookMark)}
                src="bookmarkActive.png"
                width={80}
                height={80}
                alt=""
              />
            )}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {currentNews?.map((news) => (
          <Card
            imgUrl={news["Categories"]}
            // Title={news["Title"]}
            Title={<span className="font-extrabold">{news["Title"]}</span>}
            // categories={news["Categories"]}
            categories={
              <span
                className="flex justify-center items-center"
                style={{
                  backgroundColor: "#d3d3d3",
                  color: "black",
                  fontWeight: "bold",
                  padding: "5px",
                }}
              >
                {news["Categories"]}
                {/* {newsMap[news["Categories"]]} */}
              </span>
            }
            description={
              <span>About- {news["Description"].slice(0, 60) + "..."}</span>
            }
            // description={news["Description"].slice(0, 30) + '...'}
            // negative={Math.round(parseFloat(news["Sentiment_Score"].split(' ')[1]) * 100)}
            // neutral={Math.round(parseFloat(news["Sentiment_Score"].split(' ')[2]) * 100)}
            // positive={100 - Math.round(parseFloat(news["Sentiment_Score"].split(' ')[1]) * 100) - Math.round(parseFloat(news["Sentiment_Score"].split(' ')[2]) * 100)}
            negative={
              <span style={{ textDecoration: "underline", color: "red" }}>
                {Math.round(
                  parseFloat(news["Sentiment_Score"].split(" ")[1]) * 100
                )}
              </span>
            }
            neutral={
              <span style={{ textDecoration: "underline", color: "orange" }}>
                {Math.round(
                  parseFloat(news["Sentiment_Score"].split(" ")[2]) * 100
                )}
              </span>
            }
            positive={
              <span style={{ textDecoration: "underline", color: "green" }}>
                {100 -
                  Math.round(
                    parseFloat(news["Sentiment_Score"].split(" ")[1]) * 100
                  ) -
                  Math.round(
                    parseFloat(news["Sentiment_Score"].split(" ")[2]) * 100
                  )}
              </span>
            }
            url={news["URL"]}
            updatedOn = {news['TimeStamp']}
          />
        ))}
      </div>
    </>
  );
};
//   return (
//     <>
// {/*
//       {newsData?.length > 0 ? (
//         <>
//           <div className="flex justify-center items-center">
//             <div className="flex justify-center items-center text-3xl font-bold m-6">
//               LATEST ARTICLES IN
//             </div>
//             <div className="md:flex-none w-96 order-2 sm:order-1 flex items-center justify-center py-6 sm:py-0">
//             <input
//               type="text"
//               className="input-text"
//               placeholder="Search Your Interest..."
//             />
//             <FontAwesomeIcon
//               className="-ml-7 mt-1 hover:cursor-pointer"
//               icon={faMagnifyingGlass}
//             />
//           </div>
//             <div>
//           <p>English</p>
//               {/* <Dropdown>
//                 <DropdownTrigger>
//                   <Button variant="bordered" className="capitalize">
//                     <div className="flex uppercase justify-center items-center text-3xl font-bold -ml-2">
//                     {selectedValue}
//                     <img src="/dropdown.png" className="ml-1" width={20} height = {20} alt="" />
//                     </div>
//                   </Button>
//                 </DropdownTrigger>
//                 <DropdownMenu
//                   aria-label="Single selection example"
//                   variant="flat"
//                   disallowEmptySelection
//                   selectionMode="single"
//                   selectedKeys={selectedKeys}
//                   onSelectionChange={setSelectedKeys}
//                 >
//                   <DropdownItem className="w-[100px] text-xl outline-none  hover:outline-none hover:underline" key="English">English</DropdownItem>
//                   <DropdownItem className="w-[100px] text-xl hover:outline-none hover:underline" key="Hindi">Hindi</DropdownItem>
//                 </DropdownMenu>
//               </Dropdown> */}
//             </div>
//           </div>
//           <hr className="mb-3" />

//           {selectedValue == "English" ? (
//             <>
//               <div className="grid grid-cols-3 gap-4">
//                 {newsData?.map((news) => (
//                   <Card
//                     imgUrl={news["Categories"]}
//                     // Title={news["Title"]}
//                     Title={
//                       <span className="font-extrabold">
//                         {news["Title"]}
//                       </span>
//                     }
//                     // categories={news["Categories"]}
//                     categories={
//                       <span
//                       className="flex justify-center items-center"
//                         style={{
//                           backgroundColor: "#d3d3d3",
//                           color: "black",
//                           fontWeight: "bold",
//                           padding: "5px",
//                         }}
//                       >
//                         {newsMap[news["Categories"]]}
//                       </span>
//                     }
//                     description={
//                       <span>
//                         {/* About- {news["Description"].slice(0, 30) + "..."} */}
//                       </span>
//                     }
//                     // description={news["Description"].slice(0, 30) + '...'}
//                     // negative={Math.round(parseFloat(news["Sentiment_Score"].split(' ')[1]) * 100)}
//                     // neutral={Math.round(parseFloat(news["Sentiment_Score"].split(' ')[2]) * 100)}
//                     // positive={100 - Math.round(parseFloat(news["Sentiment_Score"].split(' ')[1]) * 100) - Math.round(parseFloat(news["Sentiment_Score"].split(' ')[2]) * 100)}
//                     negative={
//                       <span
//                         style={{ textDecoration: "underline", color: "red" }}
//                       >
//                         {Math.round(
//                           // parseFloat(news["Sentiment_Score"].split(" ")[1]) *
//                             100
//                         )}
//                       </span>
//                     }
//                     neutral={
//                       <span
//                         style={{ textDecoration: "underline", color: "orange" }}
//                       >
//                         {Math.round(
//                           // parseFloat(news["Sentiment_Score"].split(" ")[2]) *
//                             100
//                         )}
//                       </span>
//                     }
//                     positive={
//                       <span
//                         style={{ textDecoration: "underline", color: "green" }}
//                       >
//                         {100 -
//                           Math.round(
//                             // parseFloat(news["Sentiment_Score"].split(" ")[1]) *
//                               100
//                           ) -
//                           Math.round(
//                             // parseFloat(news["Sentiment_Score"].split(" ")[2]) *
//                               100
//                           )}
//                       </span>
//                     }
//                     url={news["URL"]}
//                   />
//                 ))}
//               </div>
//             </>
//           ) : (
//             <>
//               <div className="grid grid-cols-3 gap-4">
//                 {regionalNews?.map((news) => (
//                   <Card
//                     imgUrl={news["Categories"]}
//                     // Title={news["Title"]}
//                     Title={
//                       <span style={{ fontWeight: "bold" }}>
//                         {news["Title"]}
//                       </span>
//                     }
//                     // categories={news["Categories"]}
//                     categories={
//                       <span
//                       className="flex justify-center items-center"
//                         style={{
//                           backgroundColor: "#d3d3d3",
//                           color: "black",
//                           fontWeight: "bold",
//                           padding: "5px",
//                         }}
//                       >
//                         {/* {newsMap[news["Categories"]]} */}
//                       </span>
//                     }
//                     description={
//                       <span>
//                         About- {news["Description"].slice(0, 30) + "..."}
//                       </span>
//                     }
//                     // description={news["Description"].slice(0, 30) + '...'}
//                     // negative={Math.round(parseFloat(news["Sentiment_Score"].split(' ')[1]) * 100)}
//                     // neutral={Math.round(parseFloat(news["Sentiment_Score"].split(' ')[2]) * 100)}
//                     // positive={100 - Math.round(parseFloat(news["Sentiment_Score"].split(' ')[1]) * 100) - Math.round(parseFloat(news["Sentiment_Score"].split(' ')[2]) * 100)}
//                     negative={
//                       <span
//                         style={{ textDecoration: "underline", color: "red" }}
//                       >
//                         {Math.round(
//                           parseFloat(news["Sentiment_Score"].split(" ")[1]) *
//                             100
//                         )}
//                       </span>
//                     }
//                     neutral={
//                       <span
//                         style={{ textDecoration: "underline", color: "orange" }}
//                       >
//                         {Math.round(
//                           parseFloat(news["Sentiment_Score"].split(" ")[2]) *
//                             100
//                         )}
//                       </span>
//                     }
//                     positive={
//                       <span
//                         style={{ textDecoration: "underline", color: "green" }}
//                       >
//                         {100 -
//                           Math.round(
//                             parseFloat(news["Sentiment_Score"].split(" ")[1]) *
//                               100
//                           ) -
//                           Math.round(
//                             parseFloat(news["Sentiment_Score"].split(" ")[2]) *
//                               100
//                           )}
//                       </span>
//                     }
//                     url={news["URL"]}
//                   />
//                 ))}
//               </div>
//             </>
//           )}
//         </>
//       ) : (
//         <>
//           <div className="flex justify-center items-center text-3xl font-bold m-6">
//             LATEST ARTICLES
//           </div>
//           <div className="md:flex-none w-96 order-2 sm:order-1 flex items-center justify-center py-6 sm:py-0">
//             <input
//               type="text"
//               className="input-text"
//               placeholder="Search Your Interest..."
//             />
//             <FontAwesomeIcon
//               className="-ml-7 mt-1 hover:cursor-pointer"
//               icon={faMagnifyingGlass}
//             />
//           </div>
//           <hr className="mb-3" />
//           <div className="flex justify-center items-center text-2xl">
//             Loading the latest articles...
//           </div>
//           {/* <div className="flex justify-center items-center space-x-8">
//             <Card imgUrl="https://source.unsplash.com/NyA2B7xovMw" />
//             <Card imgUrl="https://source.unsplash.com/2seMu5EqCDw" />
//             <Card imgUrl="https://source.unsplash.com/cHvT5F8cW50" />
//           </div> */}
//         </>
//       )} */}
//     </>
//   );
// };

export default latestPosts;

// heading, body, catgeory, url
