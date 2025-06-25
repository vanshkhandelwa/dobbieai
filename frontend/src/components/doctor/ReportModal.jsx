import React from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Box,
  Text,
  Heading,
  Divider,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  List,
  ListItem,
  ListIcon
} from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';

const ReportModal = ({ isOpen, onClose, report }) => {
  if (!report) return null;
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Doctor Report</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Heading size="md" mb={2}>Dr. {report.doctor_name}</Heading>
          <Text color="gray.600" mb={4}>
            Generated on {formatDate(report.report_date)}
          </Text>
          
          <Divider my={4} />
          
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} mb={4}>
            <Stat>
              <StatLabel>Total</StatLabel>
              <StatNumber>{report.appointment_stats.total}</StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Completed</StatLabel>
              <StatNumber>{report.appointment_stats.completed}</StatNumber>
              <StatHelpText>
                {report.appointment_stats.total 
                  ? ((report.appointment_stats.completed / report.appointment_stats.total) * 100).toFixed(1) + '%' 
                  : '0%'
                }
              </StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Scheduled</StatLabel>
              <StatNumber>{report.appointment_stats.scheduled}</StatNumber>
              <StatHelpText>
                {report.appointment_stats.total 
                  ? ((report.appointment_stats.scheduled / report.appointment_stats.total) * 100).toFixed(1) + '%' 
                  : '0%'
                }
              </StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Cancelled</StatLabel>
              <StatNumber>{report.appointment_stats.cancelled}</StatNumber>
              <StatHelpText>
                {report.appointment_stats.total 
                  ? ((report.appointment_stats.cancelled / report.appointment_stats.total) * 100).toFixed(1) + '%' 
                  : '0%'
                }
              </StatHelpText>
            </Stat>
          </SimpleGrid>
          
          {report.common_conditions && report.common_conditions.length > 0 && (
            <Box mb={4}>
              <Heading size="sm" mb={2}>Common Conditions</Heading>
              <List spacing={1}>
                {report.common_conditions.map((condition, index) => (
                  <ListItem key={index}>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    {condition.condition}: {condition.count} patients
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
          
          <Divider my={4} />
          
          <Box>
            <Heading size="sm" mb={2}>Summary</Heading>
            <Text whiteSpace="pre-wrap">{report.summary}</Text>
          </Box>
        </ModalBody>

        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={onClose}>
            Close
          </Button>
          <Button variant="ghost">Download PDF</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ReportModal;