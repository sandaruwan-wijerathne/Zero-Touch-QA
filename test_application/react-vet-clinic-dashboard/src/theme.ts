// src/theme.ts
import { createTheme } from '@mui/material/styles';

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#3f51b5', // Color primario para modo claro
    },
    secondary: {
      main: '#f50057',
    },
    error: {
      main: '#f44336',
    },
    background: {
      default: '#fafafa',
    },
  },
  typography: {
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
});

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9', // Color primario para modo oscuro
    },
    secondary: {
      main: '#f48fb1',
    },
    error: {
      main: '#f44336',
    },
    background: {
      default: '#303030',
    },
  },
  typography: {
    h2: {
      fontWeight: 700,
    },
    h3: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
});
