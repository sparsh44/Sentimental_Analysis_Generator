import { ImFacebook, ImTwitter, ImYoutube } from "react-icons/im";
import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import { useState } from "react";
import { useEffect } from "react";
import Marquee from "react-fast-marquee";

const header = () => {
  const [minutes, setMinutes] = useState("00");
  const [seconds, setSeconds] = useState("00");

  useEffect(() => {
    const currTime = new Date();
    const target = new Date(currTime.getTime() + 60 * 60000);

    const interval = setInterval(() => {
      const now = new Date();
      const difference = target.getTime() - now.getTime();
      const m = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
      setMinutes(String(m));

      const s = Math.floor((difference % (1000 * 60)) / 1000);
      let second = String(s);
      if (second.length == 1) {
        second = "0" + second;
      }
      setSeconds(second);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <header className="bg-gray-50 py-1">
        <div className="xl:container xl:mx-auto flex items-center justify-evenly sm:flex-row sm:justify-between text-center py-3">
          <img src="/logo.png" width={75} height={75} alt="" />
          <div>
            {minutes} : {seconds}
          </div>
          <div className="shrink  sm:order-2">
            <a className="font-bold uppercase text-[34px]">Community Radar</a>
          </div>
          <div className="w-96 order-3 flex justify-center items-center">
            <div className="flex gap-6">
              <div className="flex justify-evenly items-center space-x-12">
                ​​{" "}
                <a className="hover:cursor-pointer hover:scale-[1.02] duration-300 -ml-10 mr-10">
                  About
                </a>
                ​
                <a
                  href="/"
                  className="hover:cursor-pointer hover:scale-[1.02] duration-300"
                >
                  Refresh
                </a>
              </div>
              <img
                src="/policeLogo.png"
                width={75}
                height={75}
                alt=""
                className="ml-12"
              />
              <img
                src="/infosys.png"
                width={90}
                height={90}
                alt=""
              />
              {/* <a className="mt-1 hover:cursor-pointer hover:scale-[1.02] duration-300">
                <ImFacebook color="#888888" />
              </a>
              <a className="mt-1 hover:cursor-pointer hover:scale-[1.02] duration-300">
                <ImTwitter color="#888888" />
              </a>
              <a className="mt-1 hover:cursor-pointer hover:scale-[1.02] duration-300">
                <ImYoutube color="#888888" />
              </a> */}
            </div>
          </div>
        </div>
        {/* Divider */}
        <hr />
        <div className="border-white border-t-2">
          <Marquee pauseOnHover gradient={false} className="bg-[#2d5055]">
            <div className="font-bold text-xl backgroundColor text-white mt-3 flex items-center justify-center">
              Crawled over 6 websites under 10 minutes.
              Data spanning over 120+ articles.
            </div>
          </Marquee>
        </div>
      </header>
    </>
  );
};

export default header;
