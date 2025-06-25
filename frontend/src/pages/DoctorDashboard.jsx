import React, { useState, useEffect } from 'react';
import {
  Box,
  Flex,
  Heading,
  Grid,
  Button,
  useDisclosure,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Tab,
  Tabs,
  TabList,
  TabPanels,
  TabPanel,
  Card,
  CardBody,
  CardHeader
} from '@chakra-ui/react';
import { CalendarIcon, ChatIcon, RepeatIcon } from '@chakra-ui/icons';
import { useAuth } from '../contexts/AuthContext';
import { appointmentService, reportService } from '../services/api';
import ChatAssistant from '../components/common/ChatAssistant';
import NavBar from '../components/common/NavBar';
import AppointmentList from '../components/doctor/AppointmentList';
import ReportModal from '../components/doctor/ReportModal';

const DoctorDashboard = () => {
  const { user } = useAuth();
  const { isOpen: isReportOpen, onOpen: onReportOpen, onClose: onReportClose } = useDisclosure();
  const [appointments, setAppointments] = useState([]);
  const [todayAppointments, setTodayAppointments] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    scheduled: 0,
    cancelled: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isStatsLoading, setIsStatsLoading] = useState(true);
  const [report, setReport] = useState(null);
  
  useEffect(() => {
    if (user) {
      fetchAppointments();
      fetchTodayAppointments();
      fetchDoctorStats();
    }
  }, [user]);
  
  const fetchAppointments = async () => {
    try {
      setIsLoading(true);
      const response = await appointmentService.getAppointments({ doctor_id: user.id });
      setAppointments(response.data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchTodayAppointments = async () => {
    try {
      // Get today's date in YYYY-MM-DD format
      const today = new Date().toISOString().split('T')[0];
      
      const response = await appointmentService.getAppointments({ 
        doctor_id: user.id,
        from_date: today,
        to_date: today
      });
      setTodayAppointments(response.data);
    } catch (error) {
      console.error('Error fetching today\'s appointments:', error);
    }
  };
  
  const fetchDoctorStats = async () => {
    try {
      setIsStatsLoading(true);
      const response = await reportService.getDoctorStats(user.id);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching doctor stats:', error);
    } finally {
      setIsStatsLoading(false);
    }
  };
  
  const generateReport = async () => {
    try {
      const response = await reportService.generateDoctorReport({
        doctor_id: user.id,
      });
      
      setReport(response.data);
      onReportOpen();
    } catch (error) {
      console.error('Error generating report:', error);
    }
  };

  return (
    <Box>
      <NavBar />
      <Box maxW="1200px" mx="auto" px={4} py={8}>
        <Flex justifyContent="space-between" alignItems="center" mb={8}>
          <Heading>Dr. {user?.full_name}'s Dashboard</Heading>
          <Button 
            leftIcon={<RepeatIcon />} 
            colorScheme="blue" 
            onClick={generateReport}
          >
            Generate Report
          </Button>
        </Flex>
        
        {/* Stats Section */}
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6} mb={8}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Total Appointments</StatLabel>
                <StatNumber>{stats.total}</StatNumber>
              </Stat>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Completed</StatLabel>
                <StatNumber>{stats.completed}</StatNumber>
                <StatHelpText>{stats.total ? ((stats.completed / stats.total) * 100).toFixed(1) + '%' : '0%'}</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Scheduled</StatLabel>
                <StatNumber>{stats.scheduled}</StatNumber>
                <StatHelpText>{stats.total ? ((stats.scheduled / stats.total) * 100).toFixed(1) + '%' : '0%'}</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Cancelled</StatLabel>
                <StatNumber>{stats.cancelled}</StatNumber>
                <StatHelpText>{stats.total ? ((stats.cancelled / stats.total) * 100).toFixed(1) + '%' : '0%'}</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>
        
        <Grid templateColumns={{ base: "1fr", lg: "3fr 2fr" }} gap={6}>
          {/* Left side - Appointments */}
          <Box>
            <Tabs colorScheme="blue" mb={4}>
              <TabList>
                <Tab>Today's Appointments</Tab>
                <Tab>All Appointments</Tab>
              </TabList>
              <TabPanels>
                <TabPanel p={0} pt={4}>
                  <AppointmentList 
                    appointments={todayAppointments}
                    isLoading={isLoading}
                    onRefresh={() => {
                      fetchTodayAppointments();
                      fetchDoctorStats();
                    }}
                  />
                </TabPanel>
                <TabPanel p={0} pt={4}>
                  <AppointmentList 
                    appointments={appointments}
                    isLoading={isLoading}
                    onRefresh={() => {
                      fetchAppointments();
                      fetchDoctorStats();
                    }}
                  />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Box>
          
          {/* Right side - Chat Assistant */}
          <Box h="600px">
            <Heading size="md" mb={4}>Virtual Assistant</Heading>
            <ChatAssistant />
          </Box>
        </Grid>
      </Box>
      
      {/* Report Modal */}
      <ReportModal
        isOpen={isReportOpen}
        onClose={onReportClose}
        report={report}
      />
    </Box>
  );
};

export default DoctorDashboard;