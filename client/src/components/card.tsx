import React, { useState } from "react";
import style from "../styles/card.module.css";
import Image from "next/image";

interface CardProps {
  imgUrl: string;
  Title: string;
  description: string;
  positive: number;
  neutral: number;
  negative: number;
  url: string;
  updatedOn:string
}

const Card: React.FC<CardProps> = (props) => {
  const [bookMark, setBookMark] = useState(false);
  const [priority, setPriority] = useState<string[]>([]);

  const handlePriorityChange = (value: string) => {
    const updatedPriority = [...priority];

    if (updatedPriority.includes(value)) {
      // If the checkbox is already selected, deselect it
      const index = updatedPriority.indexOf(value);
      updatedPriority.splice(index, 1);
    } else {
      // If the checkbox is not selected, select it
      updatedPriority.push(value);
    }

    setPriority(updatedPriority);
  };


  function extractDateFromTimestamp(timestamp: string) {
    let parsedDate;
  
    // Check if the timestamp follows the "UPDATED: Mon DD, YYYY HH:mm IST" format
    const matchFormat1 = timestamp.match(/UPDATED: (\w{3} \d{2}, \d{4} \d{2}:\d{2} (?:AM|PM) IST)/i);
    if (matchFormat1) {
      parsedDate = new Date(matchFormat1[1]);
    } else {
      // Check if the timestamp follows the "Updated: Day, DD Month YYYY HH:mm PM (IST)" format
      const matchFormat2 = timestamp.match(/Updated: (\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2} (?:AM|PM) \(IST\))/i);
      if (matchFormat2) {
        parsedDate = new Date(matchFormat2[1]);
      } else {
        // If neither format matches, return null or handle accordingly
        return null;
      }
    }
  
    // Format the date as needed
    const formattedDate = `${parsedDate.getDate()}/${parsedDate.getMonth() + 1}/${parsedDate.getFullYear()}`;
  
    return formattedDate;
  }
  return (
    <div className="flex justify-center items-center hover:scale-[1.01] duration-300 hover:cursor-pointer">
      <div className={style.card}>
        <div className={style.card_header}>
          <Image
            src={`/categories/images/${props.imgUrl}.jpg`}
            width={400}
            height={200}
            alt="Picture of the author"
          />
        </div>
        <div className={style.card_content}>
          <h3 className="flex justify-center" id="news-title">
            {props.Title}
          </h3>
          <p className="mt-2" id="news-desc">
            {props.description}
          </p>
        </div>
        <div className="flex justify-center items-center space-x-4">
          <div className="flex flex-col justify-center items-center">
            Positive <div>{props.positive}%</div>
          </div>
          <div className="flex flex-col justify-center items-center">
            Neutral <div>{props.neutral}%</div>
          </div>
          <div className="flex flex-col justify-center items-center">
            Negative <div>{props.negative}%</div>
          </div>
        </div>
        {/* Priority Checkboxes */}
        <div className={`${style.priorityCheckboxes} flex flex-row justify-center mt-2`}>
          <label className="checkbox-label mr-4">
            <input
              type="checkbox"
              value="Critical"
              checked={priority.includes("Critical")}
              onChange={() => handlePriorityChange("Critical")}
            />
            Critical
          </label>
          <label className="checkbox-label mr-4">
            <input
              type="checkbox"
              value="High"
              checked={priority.includes("High")}
              onChange={() => handlePriorityChange("High")}
            />
            High
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              value="Low"
              checked={priority.includes("Low")}
              onChange={() => handlePriorityChange("Low")}
            />
            Low
          </label>
        </div>
        <div className="flex justify-center items-center pt-3">
          {!bookMark ? (
            <img
              className="hover:cursor-pointer mr-4"
              onClick={() => setBookMark(!bookMark)}
              src="Bookmark.png"
              width={50}
              height={50}
              alt=""
            />
          ) : (
            <img
              className="hover:cursor-pointer mr-4"
              onClick={() => setBookMark(!bookMark)}
              src="bookmarkActive.png"
              width={60}
              height={60}
              alt=""
            />
          )}
          <a
            className="text-lg hover:underline hover:scale-[1.01] duration-300"
            target="_blank"
            href={props.url}
          >
            Read More
          </a>
          {/* <label>Updated On : {extractDateFromTimestamp(props.updatedOn)}</label> */}
        </div>
      </div>
    </div>
  );
};

export default Card;
