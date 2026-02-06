// src/components/Error.tsx
import Alert from '@mui/material/Alert';

export default function Error({ children }: { children: React.ReactNode }) {
  return <Alert severity='error'>{children}</Alert>;
}
