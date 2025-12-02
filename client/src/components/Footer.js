import React from 'react';
import { Container } from 'react-bootstrap';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="text-center py-3">
      <Container>
        <p className="mb-0">
          &copy; {currentYear} PuzzleVerse - A MERN Stack Application for LLM Training
        </p>
      </Container>
    </footer>
  );
};

export default Footer;
