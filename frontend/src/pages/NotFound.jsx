import React from 'react';
import { Box, Heading, Text, Button } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const NotFound = () => {
  return (
    <Box textAlign="center" py={10} px={6}>
      <Heading
        display="inline-block"
        as="h1"
        size="4xl"
        bgGradient="linear(to-r, blue.400, blue.600)"
        backgroundClip="text"
      >
        404
      </Heading>
      <Text fontSize="18px" mt={3} mb={6}>
        Page Not Found
      </Text>
      <Text color="gray.500" mb={6}>
        The page you're looking for does not seem to exist
      </Text>

      <Button
        as={RouterLink}
        to="/"
        colorScheme="blue"
        bgGradient="linear(to-r, blue.400, blue.500, blue.600)"
        color="white"
        variant="solid"
      >
        Go to Home
      </Button>
    </Box>
  );
};

export default NotFound;