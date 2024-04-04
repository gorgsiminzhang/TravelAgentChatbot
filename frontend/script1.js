const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null;

const systemContent1 = "You are a helpful travel agent named GiggleGuide created by Simin Zhang providing travel package and infomation"; // Variable to store user's message
const API_KEY = ""; // Paste your API key here
const inputInitHeight = chatInput.scrollHeight;
const systemContent2_2 = "You are only provide mySQL query from "
const userContent2_1 = "This is mySQL table name and structure."
const userContent2_3 = "This is the data returned by my MySQL. Please process it using natural language directly:"

var Message = [];

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi; // return chat <li> element
}

const generateResponse = (chatElement) => {
    const API_URL = "https://api.openai.com/v1/chat/completions ";
    const messageElement = chatElement.querySelector("p");
    Message.push({role: "system", content: systemContent1})
    Message.push({role:"user", content: userMessage})
    // Define the properties and message for the API request
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${API_KEY}`
        },
        body: JSON.stringify({
            model: "gpt-4",
            //model: "gpt-3.5-turbo",
            messages: Message
        })
    }

    // Send POST request to API, get response and set the reponse as paragraph text
    fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
        messageElement.textContent = data.choices[0].message.content.trim();
    }).catch(() => {
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
    }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
}

const sendToBackend = (bemsg, bedir) => {   
    return fetch('http://localhost:6969/'+bedir, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        bedir: bemsg
        })
    })
    .then(response => response.json())
    .then(data => console.log(data));
}

const sendToFrontend = (fedir, msgid) => {
    return fetch('http://localhost:6969/'+fedir)
            .then(response => response.json())
            .then(data => {
                console.log(data.result); // This will be true or false
                document.getElementById(msgid).textContent= data.result;
                return data.result
                
            })
            .catch(error => console.error('Error fetching data:', error));
}

const  classifyIfSQLQuery = async(userMsg) => {
    //send userMessage to python backend to do classification
    let boolrst = null;
    await sendToBackend(userMsg, 'userInput');
    //python calculates the word embedding 
    //get bool reasult from python backend
    await sendToFrontend('get-boolean','sql-bool').then(result => {
        boolrst = result 
    });
    return boolrst
}


const generateSQLquery = async (chatElement) => {
     //get SQL database structure(parameter name) from python backend
    let dbstructure = ''
    let context = '';
    await fetch('http://localhost:6969/get-dbstructure')
    .then(response => response.json())
    .then(data => {
        console.log(data.structure); // This will be true or false
        document.getElementById('sql-structure').textContent= data.structure;
        dbstructure = data.structure;
    })
    .catch(error => console.error('Error fetching data:', error));
     
    //This function assumes userInput a is SQL related question, 
    //here we use data.structure to generate SQL query
    const API_URL = "https://api.openai.com/v1/chat/completions";
    const messageElement = chatElement.querySelector("p");
    //Message =  [{role: "system", content: systemContent2_2 + userMessage},{role: "user", content: userContent2_1 + dbstructure},]
    Message.push({role: "system", content: systemContent2_2 + userMessage})
    Message.push({role: "user", content: userContent2_1 + dbstructure},)
    // Define the properties and message for the API request
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${API_KEY}`
        },
        body: JSON.stringify({
            model: "gpt-4",
            messages: Message,
        })
    }

    
    fetch(API_URL, requestOptions).then(res => res.json()).then(async data => {
        const sqlQuery = data.choices[0].message.content.trim();
        //add assistant role to send sqlQuery to chatgpt later
        Message.push({role: "assistant", content: data.choices[0].message.content})
        // Send sqlQuery to backend
        await sendToBackend(sqlQuery,'sqlQuery').catch(error =>{
            console.error(error); 
        })

        //get SQL data and send to chatgpt later
        await sendToFrontend('get-data','sql-data').then(result => {
            Message.push({role: "user", content: userContent2_3 + result[0]})
        }).catch(error =>{
            console.error(error); 
        })

        const requestOptions = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${API_KEY}`
            },
            body: JSON.stringify({
                model: "gpt-4",
                messages: Message,
            })
        }

        await fetch(API_URL, requestOptions).then(res => res.json()).then(data =>{
            messageElement.textContent = data.choices[0].message.content.trim();
        }).catch(error =>{
            console.error(error); 
        })          
        
    }).catch(() => {
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
    }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
    
}

const handleChat = async () => {
    userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
    if(!userMessage) return;
    //add python backend to classify NL/Query Question
    classBool = await classifyIfSQLQuery(userMessage);

    // Clear the input textarea and set its height to default
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);
    
    setTimeout(() => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);

        //based on python classification bool:
        //generate NL answer if False, go to generateResponse directly
        if(classBool){
            generateSQLquery(incomingChatLi);
        }else{
            generateResponse(incomingChatLi);}
    }, 600);
}






chatInput.addEventListener("input", () => {
    // Adjust the height of the input textarea based on its content
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window 
    // width is greater than 800px, handle the chat
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});





sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));

