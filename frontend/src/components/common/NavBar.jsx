import React from 'react';
import {
  Box,
  Flex,
  Text,
  Button,
  Stack,
  Icon,
  Link,
  Popover,
  PopoverTrigger,
  PopoverContent,
  useColorModeValue,
  useDisclosure,
  useBreakpointValue,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider
} from '@chakra-ui/react';
import {
  HamburgerIcon,
  CloseIcon,
  ChevronDownIcon,
  ChevronRightIcon,
} from '@chakra-ui/icons';
import { FaUser } from 'react-icons/fa';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const NavBar = () => {
  const { isOpen, onToggle } = useDisclosure();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <Box>
      <Flex
        bg={useColorModeValue('white', 'gray.800')}
        color={useColorModeValue('gray.600', 'white')}
        minH={'60px'}
        py={{ base: 2 }}
        px={{ base: 4 }}
        borderBottom={1}
        borderStyle={'solid'}
        borderColor={useColorModeValue('gray.200', 'gray.900')}
        align={'center'}
        justify={'space-between'}
      >
        <Flex
          flex={{ base: 1, md: 'auto' }}
          ml={{ base: -2 }}
          display={{ base: 'flex', md: 'none' }}
        >
          <IconButton
            onClick={onToggle}
            icon={isOpen ? <CloseIcon w={3} h={3} /> : <HamburgerIcon w={5} h={5} />}
            variant={'ghost'}
            aria-label={'Toggle Navigation'}
          />
        </Flex>
        
        <Flex flex={{ base: 1 }} align={'center'} justify={{ base: 'center', md: 'start' }}>
          <Text
            textAlign={useBreakpointValue({ base: 'center', md: 'left' })}
            fontFamily={'heading'}
            color={useColorModeValue('gray.800', 'white')}
            fontWeight={'bold'}
            fontSize="xl"
            as={RouterLink}
            to={user?.role === 'doctor' ? '/doctor-dashboard' : '/patient-dashboard'}
          >
            DocConnect
          </Text>
        </Flex>
        
        <Stack
          flex={{ base: 1, md: 0 }}
          justify={'flex-end'}
          direction={'row'}
          spacing={6}
        >
          <Menu>
            <MenuButton
              as={Button}
              rounded={'full'}
              variant={'link'}
              cursor={'pointer'}
              minW={0}
              rightIcon={<ChevronDownIcon />}
              leftIcon={<Icon as={FaUser} />}
            >
              {user?.full_name}
            </MenuButton>
            <MenuList>
              <MenuItem
                as={RouterLink}
                to={user?.role === 'doctor' ? '/doctor-dashboard' : '/patient-dashboard'}
              >
                Dashboard
              </MenuItem>
              <MenuItem as={RouterLink} to="/profile">
                Profile
              </MenuItem>
              <MenuDivider />
              <MenuItem onClick={handleLogout}>Sign Out</MenuItem>
            </MenuList>
          </Menu>
        </Stack>
      </Flex>
    </Box>
  );
};

export default NavBar;