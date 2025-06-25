import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  VStack, 
  Input, 
  Button, 
  Text, 
  Flex, 
  Avatar, 
  Spinner, 
  IconButton,
  Heading
} from '@chakra-ui/react';
import { ArrowUpIcon, DeleteIcon } from '@chakra-ui/icons';
import ReactMarkdown from 'react-markdown';
import { chatService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const ChatAssistant = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message to conversation
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, { text: input, sender: 'user' }]);
    setInput('');
    setIsLoading(true);

    try {
      // Update conversation history with user message
      const updatedHistory = [...conversationHistory, userMessage];

      // Send message to AI assistant
      const response = await chatService.sendMessage(
        input,
        updatedHistory,
        user?.id,
        user?.role
      );

      // Get AI response
      const assistantMessage = response.data.response;
      
      // Update messages state with assistant response
      setMessages(prev => [...prev, { text: assistantMessage, sender: 'assistant' }]);
      
      // Update conversation history
      setConversationHistory(response.data.conversation_history);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { 
        text: 'Sorry, there was an error processing your request. Please try again.', 
        sender: 'assistant',
        error: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setConversationHistory([]);
  };

  return (
    <Box borderWidth="1px" borderRadius="lg" overflow="hidden" h="100%">
      <Flex direction="column" h="100%">
        {/* Header */}
        <Flex 
          bg="blue.500" 
          color="white" 
          p={3} 
          alignItems="center" 
          justifyContent="space-between"
        >
          <Heading size="md">Assistant</Heading>
          <IconButton
            icon={<DeleteIcon />}
            variant="ghost"
            colorScheme="whiteAlpha"
            onClick={clearChat}
            aria-label="Clear chat"
          />
        </Flex>
        
        {/* Chat Messages */}
        <VStack 
          flex="1" 
          overflowY="auto" 
          p={4} 
          spacing={4}
          alignItems="stretch"
        >
          {messages.length === 0 && (
            <Text color="gray.500" textAlign="center" py={10}>
              How can I help you today?
            </Text>
          )}
          
          {messages.map((message, index) => (
            <Flex 
              key={index}
              justify={message.sender === 'user' ? 'flex-end' : 'flex-start'}
              mb={2}
            >
              {message.sender !== 'user' && (
                <Avatar size="sm" name="AI Assistant" bg="blue.500" mr={2} />
              )}
              
              <Box
                maxW="80%"
                bg={message.sender === 'user' ? 'blue.100' : 'gray.100'}
                color={message.error ? 'red.500' : 'black'}
                py={2}
                px={4}
                borderRadius="lg"
              >
                {message.sender === 'user' ? (
                  <Text>{message.text}</Text>
                ) : (
                  <Box className="markdown-body">
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                  </Box>
                )}
              </Box>
              
              {message.sender === 'user' && (
                <Avatar size="sm" name={user?.full_name || 'User'} ml={2} />
              )}
            </Flex>
          ))}
          
          {isLoading && (
            <Flex justify="flex-start" mb={2}>
              <Avatar size="sm" name="AI Assistant" bg="blue.500" mr={2} />
              <Box p={2} borderRadius="lg" bg="gray.100">
                <Spinner size="sm" mr={2} />
                <Text as="span">Thinking...</Text>
              </Box>
            </Flex>
          )}
          
          <div ref={messagesEndRef} />
        </VStack>
        
        {/* Input Area */}
        <Flex p={2} borderTopWidth="1px">
          <Input
            flex="1"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            mr={2}
          />
          <Button
            colorScheme="blue"
            onClick={handleSend}
            isLoading={isLoading}
            leftIcon={<ArrowUpIcon />}
          >
            Send
          </Button>
        </Flex>
      </Flex>
    </Box>
  );
};

export default ChatAssistant;