import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Heading,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Grid,
  Button,
  useDisclosure,
  Text,
  Badge
} from '@chakra-ui/react';
import { CalendarIcon, ChatIcon } from '@chakra-ui/icons';
import { useAuth } from '../contexts/AuthContext';
import { appointmentService } from '../services/api';
import ChatAssistant from '../components/common/ChatAssistant';
import NavBar from '../components/common/NavBar';
import AppointmentList from '../components/patient/AppointmentList';

const PatientDashboard = () => {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    if (user) {
      fetchAppointments();
    }
  }, [user]);
  
  const fetchAppointments = async () => {
    try {
      setIsLoading(true);
      const response = await appointmentService.getAppointments({ patient_id: user.id });
      setAppointments(response.data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleCancelAppointment = async (appointmentId) => {
    try {
      await appointmentService.cancelAppointment(appointmentId);
      fetchAppointments(); // Refresh appointments
    } catch (error) {
      console.error('Error cancelling appointment:', error);
    }
  };

  return (
    <Box>
      <NavBar />
      <Box maxW="1200px" mx="auto" px={4} py={8}>
        <Flex justifyContent="space-between" alignItems="center" mb={8}>
          <Heading>Welcome, {user?.full_name}</Heading>
        </Flex>
        
        <Grid templateColumns={{ base: "1fr", lg: "3fr 2fr" }} gap={6}>
          {/* Left side - Appointments */}
          <Box>
            <Heading size="md" mb={4}>Your Appointments</Heading>
            <AppointmentList 
              appointments={appointments}
              isLoading={isLoading}
              onCancelAppointment={handleCancelAppointment}
              onRefresh={fetchAppointments}
            />
          </Box>
          
          {/* Right side - Chat Assistant */}
          <Box h="600px">
            <Heading size="md" mb={4}>Virtual Assistant</Heading>
            <ChatAssistant />
          </Box>
        </Grid>
      </Box>
    </Box>
  );
};

export default PatientDashboard;