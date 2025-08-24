import React, { useState } from "react";
import axios from "axios";
import sendBtn from "../assets/send.svg";

const AskQuestion = ({ sessionId, saveChat, addQuestionToChat }) => {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const handleQuestionChange = (event) => {
    setQuestion(event.target.value);
  };

  // Accept an event so we can preventDefault when called from form submit
  const handleAsk = async (event) => {
    if (event && event.preventDefault) event.preventDefault();
    if (loading) return;
    if (!question.trim()) return;

    const currentQuestion = question;
    setQuestion("");
    setLoading(true);

    const tempChat = {
      sessionId,
      question: currentQuestion,
      response: "Loading...",
    };
    addQuestionToChat(tempChat);

    try {
      const res = await axios.post("http://127.0.0.1:5000/ask_question", {
        question: currentQuestion,
        session_id: sessionId,
      });

      saveChat({ question: currentQuestion, response: res.data.response });
      addQuestionToChat(
        { sessionId, question: currentQuestion, response: res.data.response },
        true
      );
    } catch (error) {
      console.error("Error asking question:", error);
      addQuestionToChat(
        {
          sessionId,
          question: currentQuestion,
          response: "Error fetching response",
        },
        true
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatFooter">
      {/* Use a form so Enter triggers onSubmit */}
      <form className="inp" onSubmit={handleAsk}>
        <input
          type="text"
          value={question}
          onChange={handleQuestionChange}
          placeholder="Ask a question"
          autoComplete="off"
        />
        <button className="send" type="submit" disabled={loading}>
          {loading ? (
            <div className="spinner"></div>
          ) : (
            <img src={sendBtn} alt="Send" />
          )}
        </button>
      </form>
    </div>
  );
};

export default AskQuestion;


// import React, { useState } from "react";
// import axios from "axios";
// import sendBtn from "../assets/send.svg";

// const AskQuestion = ({ sessionId, saveChat, addQuestionToChat }) => {
//   const [question, setQuestion] = useState("");
//   const [loading, setLoading] = useState(false);

//   const handleQuestionChange = (event) => {
//     setQuestion(event.target.value);
//   };

//   const handleAsk = async () => {
//     if (!question.trim()) return;

//     const currentQuestion = question;
//     setQuestion("");

//     setLoading(true);

//     const tempChat = {
//       sessionId,
//       question: currentQuestion,
//       response: "Loading...",
//     };
//     addQuestionToChat(tempChat);

//     try {
//       const res = await axios.post("http://127.0.0.1:5000/ask_question", {
//         question: currentQuestion,
//         session_id: sessionId,
//       });

//       saveChat({ question: currentQuestion, response: res.data.response });
//       addQuestionToChat(
//         { sessionId, question: currentQuestion, response: res.data.response },
//         true
//       );
//     } catch (error) {
//       console.error("Error asking question:", error);
//       addQuestionToChat(
//         {
//           sessionId,
//           question: currentQuestion,
//           response: "Error fetching response",
//         },
//         true
//       );
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="chatFooter">
//       <div className="inp">
//         <input
//           type="text"
//           value={question}
//           onChange={handleQuestionChange}
//           placeholder="Ask a question"
//         />
//         <button
//           className="send"
//           onClick={handleAsk}
//           disabled={loading}
//           onKeyDown={(e) => {
//             if (e.key === "Enter") {
//               e.preventDefault();
//               handleAsk();
//             }
//           }}
//         >
//           {loading ? (
//             <div className="spinner"></div>
//           ) : (
//             <img src={sendBtn} alt="Send" />
//           )}
//         </button>
//       </div>
//       {/* <br /> */}
//     </div>
//   );
// };

// export default AskQuestion;
