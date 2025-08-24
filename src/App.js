import React, { useState, useEffect } from "react";
import axios from "axios";
import { openDB } from "idb";
import AskQuestion from "./components/AskQuestion";
import "./App.css";
import gptLogo from "./assets/law1.png";
import njdg from "./assets/njdg.png";
import statusLogo from "./assets/status.png";
import settleLogo from "./assets/settle.png";
import addBtn from "./assets/add-30.png";
import msgIcon from "./assets/message.svg";
import userIcon from "./assets/user2.png";
import gptImgLogo from "./assets/gptimg1.png";
import FeedbackPopup from "./components/FeedbackPopup";

// Initialize IndexedDB
const initDB = async () => {
  const db = await openDB("chatAppDB", 1, {
    upgrade(db) {
      // Create a store for chats
      const chatsStore = db.createObjectStore("chats", {
        keyPath: "id",
        autoIncrement: true,
      });
      chatsStore.createIndex("sessionIdIndex", "sessionId");

      // Create a store for sessions
      const sessionsStore = db.createObjectStore("sessions", {
        keyPath: "sessionId",
      });
      sessionsStore.createIndex("timestampIndex", "timestamp");
    },
  });
  return db;
};

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [db, setDb] = useState(null);
  const [previousChats, setPreviousChats] = useState([]);
  const [availableSessions, setAvailableSessions] = useState([]);
  const [chatName, setChatName] = useState("");
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  useEffect(() => {
    const setupDB = async () => {
      const dbInstance = await initDB();
      setDb(dbInstance);

      const storedSessionId = localStorage.getItem("session_id");
      if (storedSessionId) {
        setSessionId(storedSessionId);
      }

      const sessions = await dbInstance.getAllFromIndex(
        "sessions",
        "timestampIndex"
      );
      setAvailableSessions(sessions.reverse().map((s) => s.sessionId));

      if (sessionId) {
        const storedChats = await dbInstance.getAllFromIndex(
          "chats",
          "sessionIdIndex",
          sessionId
        );
        setPreviousChats(storedChats);

        if (sessions.length > 0) {
          setChatName(
            `Chat ${
              availableSessions.length - availableSessions.indexOf(sessionId)
            }`
          );
        }
      }
    };
    setupDB();
  }, [sessionId]);

  const saveChatToIndexedDB = async (chat) => {
    if (db && sessionId) {
      chat.sessionId = sessionId;
      await db.add("chats", chat);
      const updatedChats = await db.getAllFromIndex(
        "chats",
        "sessionIdIndex",
        sessionId
      );
      setPreviousChats(updatedChats);

      if (updatedChats.length === 1) {
        setChatName(
          `Chat ${
            availableSessions.length - availableSessions.indexOf(sessionId)
          }`
        );
      }
    }
  };

  const startNewChat = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/new_chat");
      const newSessionId = response.data.session_id;
      setSessionId(newSessionId);
      localStorage.setItem("session_id", newSessionId);
      console.log("New chat started with session ID:", newSessionId);

      if (db) {
        await db.add("sessions", {
          sessionId: newSessionId,
          timestamp: Date.now(),
        });
        const sessions = await db.getAllFromIndex("sessions", "timestampIndex");
        setAvailableSessions(sessions.reverse().map((s) => s.sessionId));
      }
    } catch (error) {
      console.error("Error starting new chat:", error);
    }
  };

  const fetchChatsForSession = async (sessionId) => {
    if (db && sessionId) {
      const storedChats = await db.getAllFromIndex(
        "chats",
        "sessionIdIndex",
        sessionId
      );
      setPreviousChats(storedChats);
      console.log("Loaded previous chats for session:", sessionId);

      setSessionId(sessionId);
      localStorage.setItem("session_id", sessionId);
    }
  };

  const addQuestionToChat = (chat, update = false) => {
    setPreviousChats((prevChats) => {
      if (update) {
        return prevChats.map((c) => (c.question === chat.question ? chat : c));
      } else {
        return [...prevChats, chat];
      }
    });
  };

  const deleteSession = async (sessionId) => {
    try {
      if (db) {
        const tx = db.transaction(["sessions", "chats"], "readwrite");
        const sessionsStore = tx.objectStore("sessions");
        const chatsStore = tx.objectStore("chats");

        // Delete the session
        await sessionsStore.delete(sessionId);

        // Delete associated chats
        const allChats = await chatsStore.getAll();
        const sessionChats = allChats.filter(
          (chat) => chat.sessionId === sessionId
        );
        for (let chat of sessionChats) {
          await chatsStore.delete(chat.id);
        }

        await tx.done;

        const sessions = await db.getAllFromIndex("sessions", "timestampIndex");
        setAvailableSessions(sessions.reverse().map((s) => s.sessionId));

        if (sessionId === localStorage.getItem("session_id")) {
          localStorage.removeItem("session_id");
          setSessionId(null);
          setPreviousChats([]);
        }
      }
    } catch (error) {
      console.error("Error deleting session:", error);
    }
  };

  const handleFeedbackSubmit = (feedback) => {
    console.log("User Feedback:", feedback);
    // Save feedback to a database or handle it as needed
    alert("Thank you for your feedback!");
  };

  return (
    <div className="App">
      <div className="sideBar">
        <div className="upperSide">
          <div className="upperSideTop">
            <img src={gptLogo} alt="Logo" className="logo" />
            <span className="brand">Justice Genie</span>
          </div>
          <button className="midBtn" onClick={startNewChat}>
            <img src={addBtn} alt="new chat" className="addBtn" />
            New Chat
          </button>
          <button
            className="midBtn linkBtn"
            onClick={() =>
              window.open(
                "https://doj.gov.in/national-judicial-data-grid-2/",
                "_blank"
              )
            }
          >
            <img src={njdg} alt="Logo" className="logo" />
            National Judicial Data Grid
          </button>
          <button
            className="midBtn linkBtn"
            onClick={() =>
              window.open(
                "https://services.ecourts.gov.in/ecourtindia_v6/",
                "_blank"
              )
            }
          >
            <img src={statusLogo} alt="Logo" className="logo" />
            Know Your Case Status
          </button>
          <button
            className="midBtn linkBtn"
            onClick={() =>
              window.open("https://vcourts.gov.in/virtualcourt/", "_blank")
            }
          >
            <img src={settleLogo} alt="Logo" className="logo" />
            Settle Your Traffic Violation
          </button>
        </div>
        <div className="lowerSide">
          {availableSessions.map((id, index) => (
            <div key={id} className="sessionItem">
              <button
                className="query"
                onClick={() => fetchChatsForSession(id)}
              >
                <img src={msgIcon} alt="Query" />
                Chat {availableSessions.length - index}
              </button>
              <button className="deleteBtn" onClick={() => deleteSession(id)}>
                🗑️
              </button>
            </div>
          ))}
        </div>
      </div>
      <div className="main">
        <div className="chats">
          <div className="chatHeader">{chatName}</div>
          {previousChats.map((chat) => (
            <div key={chat.id} className="chat">
              <div className="chat user">
                <img className="chatimg t1" src={userIcon} alt="User Icon" />
                <div className="txt">
                  <strong>Question:</strong> {chat.question}
                </div>
                <small>{chat.timestamp}</small>
              </div>
              <div key={`response-${chat.id}`} className="chat bot">
                <img className="chatimg t2" src={gptImgLogo} alt="GPT Logo" />
                <div className="txt">
                  <strong>Response</strong> <pre>{chat.response}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
        {/* <FeedbackPopup */}
        {/* isOpen={isFeedbackOpen}
        onClose={() => setIsFeedbackOpen(false)}
        onSubmitFeedback={handleFeedbackSubmit}
      /> */}

        <div className="chatFooter">
          {sessionId && (
            <>
              <AskQuestion
                sessionId={sessionId}
                saveChat={saveChatToIndexedDB}
                addQuestionToChat={addQuestionToChat}
              />
              {/* <button
        className="feedbackBtn"
        onClick={() => setIsFeedbackOpen(true)}
        title="Provide Feedback"
      >
        Feedback
      </button> */}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
